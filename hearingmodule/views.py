from datetime import datetime
from pathlib import Path

from django.contrib import messages
from django.db import transaction
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone
from django.views.decorators.http import require_POST

from complaints.models import Complaint
from residentmodule.models import Resident
from bantaybarangay.security import role_required
from .models import (
    Hearing,
    HearingAttachment,
    HearingMinutesDocument,
)
from registration.models import User

from .services.hearing_minutes_pdf import (
    generate_hearing_minutes_pdf,
)

# =========================================================
# CONFIGURATION
# =========================================================

ALLOWED_HEARING_STAGES = [
    "Mediation",
    "Conciliation",
    "Pangkat",
    "Arbitration",
    "Settlement",
]

ALLOWED_HEARING_STATUSES = [
    "Scheduled",
    "In Progress",
    "Completed",
    "Postponed",
    "Cancelled",
]

ALLOWED_ATTACHMENT_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",

    ".mp3",
    ".wav",
    ".ogg",
    ".m4a",
    ".aac",

    ".pdf",
    ".doc",
    ".docx",
    ".txt",
}

MAX_ATTACHMENT_SIZE = 25 * 1024 * 1024


# =========================================================
# REDIRECT HELPER
# =========================================================

def hearing_redirect():

    return redirect(
        "hearingmodule:hearing_schedule"
    )


# =========================================================
# CURRENT USER
# =========================================================

def get_current_user_id(request):

    user_id = request.session.get(
        "user_id"
    )

    if not user_id:
        return None

    try:
        return int(user_id)

    except (
        TypeError,
        ValueError,
    ):
        return None


# =========================================================
# COMPLAINT ASSIGNED USER ID
# =========================================================

def get_complaint_assigned_user_id(
    complaint
):

    """
    Supports either:

    assigned_official = IntegerField()

    OR

    assigned_official = ForeignKey(...)
    """

    assigned_id = getattr(
        complaint,
        "assigned_official_id",
        None,
    )

    if assigned_id is not None:

        try:
            return int(assigned_id)

        except (
            TypeError,
            ValueError,
        ):
            pass

    assigned_official = getattr(
        complaint,
        "assigned_official",
        None,
    )

    if assigned_official is None:
        return None

    # ForeignKey object
    object_user_id = getattr(
        assigned_official,
        "user_id",
        None,
    )

    if object_user_id is not None:

        try:
            return int(object_user_id)

        except (
            TypeError,
            ValueError,
        ):
            return None

    # Integer / numeric value
    try:
        return int(assigned_official)

    except (
        TypeError,
        ValueError,
    ):
        return None


# =========================================================
# COMPLAINT OWNERSHIP
# =========================================================

def user_can_manage_complaint(
    request,
    complaint
):

    current_user_id = (
        get_current_user_id(
            request
        )
    )

    if not current_user_id:
        return False

    assigned_user_id = (
        get_complaint_assigned_user_id(
            complaint
        )
    )

    if not assigned_user_id:
        return False

    return (
        current_user_id
        ==
        assigned_user_id
    )


# =========================================================
# RESIDENT NAME
# =========================================================

def get_resident_name(
    resident_id
):

    try:

        resident = Resident.objects.get(
            resident_id=resident_id
        )

    except Resident.DoesNotExist:

        return (
            f"Resident #{resident_id}"
        )

    # -----------------------------------------------------
    # Direct full-name fields
    # -----------------------------------------------------

    for field_name in [
        "full_name",
        "fullname",
        "resident_name",
        "name",
    ]:

        if hasattr(
            resident,
            field_name
        ):

            value = getattr(
                resident,
                field_name
            )

            if value:

                return str(
                    value
                ).strip()

    # -----------------------------------------------------
    # Construct name
    # -----------------------------------------------------

    name_parts = []

    field_groups = [

        [
            "first_name",
            "firstname",
            "given_name",
        ],

        [
            "middle_name",
            "middlename",
        ],

        [
            "last_name",
            "lastname",
            "surname",
        ],

        [
            "suffix",
            "suffix_name",
        ],
    ]

    for possible_fields in field_groups:

        value = ""

        for field_name in possible_fields:

            if hasattr(
                resident,
                field_name
            ):

                field_value = getattr(
                    resident,
                    field_name
                )

                if field_value:

                    value = str(
                        field_value
                    ).strip()

                    break

        if value:

            name_parts.append(
                value
            )

    if name_parts:

        return " ".join(
            name_parts
        )

    return (
        f"Resident #{resident_id}"
    )


# =========================================================
# HEARING SCHEDULE PAGE
# =========================================================
@role_required("admin", "official")
def hearing_schedule(request):

    today = timezone.localdate()

    # -----------------------------------------------------
    # Complaints whose workflow reached Hearing Scheduled
    # -----------------------------------------------------

    hearing_complaints = (
        Complaint.objects
        .filter(
            status="Hearing Scheduled"
        )
        .order_by(
            "-updated_at"
        )
    )

    # -----------------------------------------------------
    # All hearing records
    #
    # Important:
    # We keep completed / in-progress hearings visible even
    # when the complaint status changes to Under Mediation.
    # -----------------------------------------------------

    existing_hearings = (
        Hearing.objects
        .all()
        .order_by(
            "hearing_date",
            "start_time",
            "hearing_id",
        )
    )

    # -----------------------------------------------------
    # Complaint IDs
    # -----------------------------------------------------

    complaint_ids = set(
        existing_hearings.values_list(
            "complaint_id",
            flat=True,
        )
    )

    complaint_ids.update(
        hearing_complaints.values_list(
            "complaint_id",
            flat=True,
        )
    )

    # -----------------------------------------------------
    # Complaint lookup
    # -----------------------------------------------------

    complaints = (
        Complaint.objects
        .filter(
            complaint_id__in=
                complaint_ids
        )
    )

    complaint_map = {
        complaint.complaint_id:
            complaint

        for complaint in complaints
    }

    # -----------------------------------------------------
    # Complaints that already have active hearings
    # -----------------------------------------------------

    complaints_with_active_hearing = set(
        existing_hearings
        .filter(
            status__in=[
                "Scheduled",
                "In Progress",
                "Postponed",
            ]
        )
        .values_list(
            "complaint_id",
            flat=True,
        )
    )

    # -----------------------------------------------------
    # Only show complaints that still need scheduling
    # -----------------------------------------------------

    schedulable_complaints = []

    for complaint in hearing_complaints:

        if (
            complaint.complaint_id
            in
            complaints_with_active_hearing
        ):
            continue

        # Only the assigned handler should be able
        # to schedule the complaint.

        if not user_can_manage_complaint(
            request,
            complaint
        ):
            continue

        schedulable_complaints.append(
            complaint
        )

        # -----------------------------------------------------
    # Build hearing records
    # -----------------------------------------------------

    hearing_records = []

    for hearing in existing_hearings:

        complaint = complaint_map.get(
            hearing.complaint_id
        )

        can_manage = False

        if complaint:

            can_manage = (
                user_can_manage_complaint(
                    request,
                    complaint
                )
            )

        # -------------------------------------------------
        # Official Hearing Minutes document
        # -------------------------------------------------

        hearing_minutes_document = (
            HearingMinutesDocument.objects
            .filter(
                hearing_id=hearing.hearing_id,
                document_type="HEARING_MINUTES",
            )
            .order_by(
                "-document_id"
            )
            .first()
        )

        hearing_records.append(
            {
                "hearing":
                    hearing,

                "complaint":
                    complaint,

                "can_manage":
                    can_manage,

                "hearing_minutes_document":
                    hearing_minutes_document,
            }
        )

    # -----------------------------------------------------
    # Today's hearings
    # -----------------------------------------------------

    today_hearings = (
        existing_hearings
        .filter(
            hearing_date=today
        )
    )

    today_count = (
        today_hearings.count()
    )

    in_progress_count = (
        today_hearings
        .filter(
            status="In Progress"
        )
        .count()
    )

    upcoming_today_count = (
        today_hearings
        .filter(
            status="Scheduled"
        )
        .count()
    )

    # -----------------------------------------------------
    # Active mediations
    # -----------------------------------------------------

    active_mediations = (
        existing_hearings
        .filter(
            hearing_stage__in=[
                "Mediation",
                "Conciliation",
                "Pangkat",
            ],
            status__in=[
                "Scheduled",
                "In Progress",
                "Postponed",
            ],
        )
        .count()
    )

    # -----------------------------------------------------
    # Summons statistics
    # -----------------------------------------------------

    summons_served = (
        existing_hearings
        .filter(
            summons_status="Served"
        )
        .count()
    )

    summons_pending = (
        existing_hearings
        .filter(
            summons_status="Pending"
        )
        .count()
    )

    total_summons = (
        existing_hearings.count()
    )

    if total_summons:

        summons_percentage = round(
            (
                summons_served
                /
                total_summons
            )
            * 100,
            1,
        )

    else:

        summons_percentage = 0

    # -----------------------------------------------------
    # Completed
    # -----------------------------------------------------

    completed_count = (
        existing_hearings
        .filter(
            status="Completed"
        )
        .count()
    )

    # -----------------------------------------------------
    # Context
    # -----------------------------------------------------

    context = {

        "hearing_records":
            hearing_records,

        "hearing_complaints":
            schedulable_complaints,

        "calendar_hearings":
            existing_hearings,

        "today":
            today,

        "today_count":
            today_count,

        "in_progress_count":
            in_progress_count,

        "upcoming_today_count":
            upcoming_today_count,

        "active_mediations":
            active_mediations,

        "summons_served":
            summons_served,

        "summons_pending":
            summons_pending,

        "summons_percentage":
            summons_percentage,

        "completed_count":
            completed_count,

        "total_hearing_records":
            existing_hearings.count(),
    }

    return render(
        request,
        "hearingmodule/hearing_schedule.html",
        context,
    )


# =========================================================
# CREATE HEARING
# =========================================================
@role_required("admin", "official")
@require_POST
@transaction.atomic
def create_hearing(request):

    complaint_id = request.POST.get(
        "complaint_id"
    )

    hearing_date = request.POST.get(
        "hearing_date",
        "",
    ).strip()

    start_time = request.POST.get(
        "start_time",
        "",
    ).strip()

    end_time = request.POST.get(
        "end_time",
        "",
    ).strip()

    chamber = request.POST.get(
        "chamber",
        "",
    ).strip()

    hearing_stage = request.POST.get(
        "hearing_stage",
        "Mediation",
    ).strip()

    mediator = request.POST.get(
        "mediator",
        "",
    ).strip()

    notes = request.POST.get(
        "notes",
        "",
    ).strip()

    # -----------------------------------------------------
    # Complaint ID
    # -----------------------------------------------------

    if not complaint_id:

        messages.error(
            request,
            "Please select a complaint."
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Lock complaint while scheduling
    # -----------------------------------------------------

    complaint = get_object_or_404(
        Complaint.objects.select_for_update(),
        complaint_id=complaint_id,
    )

    # -----------------------------------------------------
    # Complaint status
    # -----------------------------------------------------

    if complaint.status != "Hearing Scheduled":

        messages.error(
            request,
            (
                "This complaint is not currently "
                "ready for hearing scheduling."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Ownership
    # -----------------------------------------------------

    if not user_can_manage_complaint(
        request,
        complaint
    ):

        messages.error(
            request,
            (
                "You cannot schedule this hearing "
                "because the complaint is assigned "
                "to another Admin or Barangay Official."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Existing active hearing
    # -----------------------------------------------------

    active_exists = (
        Hearing.objects
        .filter(
            complaint_id=
                complaint.complaint_id,
            status__in=[
                "Scheduled",
                "In Progress",
                "Postponed",
            ],
        )
        .exists()
    )

    if active_exists:

        messages.error(
            request,
            (
                "This complaint already has "
                "an active hearing."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Required fields
    # -----------------------------------------------------

    if (
        not hearing_date
        or
        not start_time
        or
        not end_time
        or
        not chamber
    ):

        messages.error(
            request,
            (
                "Please complete all required "
                "hearing fields."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Parse date
    # -----------------------------------------------------

    try:

        parsed_date = datetime.strptime(
            hearing_date,
            "%Y-%m-%d",
        ).date()

    except ValueError:

        messages.error(
            request,
            "Invalid hearing date."
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Past date validation
    # -----------------------------------------------------

    if parsed_date < timezone.localdate():

        messages.error(
            request,
            (
                "The hearing date cannot "
                "be in the past."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Parse times
    # -----------------------------------------------------

    try:

        parsed_start = datetime.strptime(
            start_time,
            "%H:%M",
        ).time()

        parsed_end = datetime.strptime(
            end_time,
            "%H:%M",
        ).time()

    except ValueError:

        messages.error(
            request,
            "Invalid hearing time."
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Time validation
    # -----------------------------------------------------

    if parsed_end <= parsed_start:

        messages.error(
            request,
            (
                "End time must be later "
                "than start time."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Stage validation
    # -----------------------------------------------------

    if (
        hearing_stage
        not in
        ALLOWED_HEARING_STAGES
    ):

        messages.error(
            request,
            "Invalid hearing stage."
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Chamber conflict
    #
    # Existing start < requested end
    # Existing end   > requested start
    # -----------------------------------------------------

    chamber_conflict = (
        Hearing.objects
        .filter(
            hearing_date=
                parsed_date,

            chamber=
                chamber,

            status__in=[
                "Scheduled",
                "In Progress",
                "Postponed",
            ],

            start_time__lt=
                parsed_end,

            end_time__gt=
                parsed_start,
        )
        .exists()
    )

    if chamber_conflict:

        messages.error(
            request,
            (
                "The selected chamber already "
                "has another hearing during "
                "that time."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Case number
    # -----------------------------------------------------

    case_number = (
        f"KP-{parsed_date.year}-"
        f"{complaint.complaint_id:04d}"
    )

    # -----------------------------------------------------
    # Complainant name
    # -----------------------------------------------------

    complainant_name = get_resident_name(
        complaint.resident_id
    )

    # -----------------------------------------------------
    # Respondent name
    # -----------------------------------------------------

    respondent_name = (
        getattr(
            complaint,
            "respondent_name",
            None,
        )
        or
        "N/A"
    )

    # -----------------------------------------------------
    # Dispute nature
    # -----------------------------------------------------

    dispute_nature = (
        getattr(
            complaint,
            "complaint_type",
            None,
        )
        or
        "Complaint"
    )

    # -----------------------------------------------------
    # Create hearing
    # -----------------------------------------------------

    Hearing.objects.create(

        resident_id=
            complaint.resident_id,

        complaint_id=
            complaint.complaint_id,

        case_number=
            case_number,

        complainant_name=
            complainant_name,

        respondent_name=
            respondent_name,

        dispute_nature=
            dispute_nature,

        hearing_date=
            parsed_date,

        start_time=
            parsed_start,

        end_time=
            parsed_end,

        chamber=
            chamber,

        mediator=
            mediator
            or
            None,

        summons_status=
            "Pending",

        hearing_stage=
            hearing_stage,

        status=
            "Scheduled",

        notes=
            notes
            or
            None,
    )

    messages.success(
        request,
        (
            f"Hearing for complaint "
            f"#CP-{complaint.complaint_id:04d} "
            f"was scheduled successfully."
        )
    )

    return hearing_redirect()


# =========================================================
# START HEARING
# =========================================================
@role_required("admin", "official")
@require_POST
@transaction.atomic
def start_hearing(
    request,
    hearing_id
):

    hearing = get_object_or_404(
        Hearing.objects.select_for_update(),
        hearing_id=hearing_id,
    )

    complaint = get_object_or_404(
        Complaint.objects.select_for_update(),
        complaint_id=hearing.complaint_id,
    )

    # -----------------------------------------------------
    # Ownership
    # -----------------------------------------------------

    if not user_can_manage_complaint(
        request,
        complaint
    ):

        messages.error(
            request,
            (
                "You cannot start this hearing "
                "because the complaint is assigned "
                "to another Admin or Barangay Official."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    if hearing.status != "Scheduled":

        messages.error(
            request,
            (
                "Only a scheduled hearing "
                "can be started."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Scheduled date
    # -----------------------------------------------------

    today = timezone.localdate()

    if hearing.hearing_date != today:

        messages.error(
            request,
            (
                "This hearing can only be started "
                "on its scheduled hearing date."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Start
    #
    # Your MySQL table has no started_at column.
    # -----------------------------------------------------

    hearing.status = "In Progress"

    hearing.save(
        update_fields=[
            "status",
        ]
    )

    # -----------------------------------------------------
    # Complaint workflow
    # -----------------------------------------------------

    complaint.status = "Under Mediation"
    complaint.updated_at = timezone.now()

    complaint.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    messages.success(
        request,
        (
            f"{hearing.case_number} "
            f"is now in progress."
        )
    )

    return hearing_redirect()


# =========================================================
# COMPLETE HEARING
# =========================================================
@role_required("admin", "official")
@require_POST
@transaction.atomic
def complete_hearing(
    request,
    hearing_id
):

    hearing = get_object_or_404(
        Hearing.objects.select_for_update(),
        hearing_id=hearing_id,
    )

    complaint = get_object_or_404(
        Complaint.objects.select_for_update(),
        complaint_id=hearing.complaint_id,
    )

    # -----------------------------------------------------
    # Ownership
    # -----------------------------------------------------

    if not user_can_manage_complaint(
        request,
        complaint
    ):

        messages.error(
            request,
            (
                "You cannot complete this hearing "
                "because the complaint is assigned "
                "to another Admin or Barangay Official."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    if hearing.status != "In Progress":

        messages.error(
            request,
            (
                "Only an in-progress hearing "
                "can be completed."
            )
        )

        return hearing_redirect()

        # -----------------------------------------------------
    # Hearing notes are required before completion
    # -----------------------------------------------------

    if not hearing.notes or not hearing.notes.strip():

        messages.error(
            request,
            (
                "Please record and save the Hearing Notes / "
                "Minutes before completing the hearing."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Complete
    #
    # Your MySQL table has no completed_at column.
    # -----------------------------------------------------

    hearing.status = "Completed"

    hearing.save(
        update_fields=[
            "status",
        ]
    )

    # -----------------------------------------------------
    # Complaint intentionally stays Under Mediation.
    #
    # Completing a hearing does not necessarily mean the
    # barangay complaint itself has been settled/resolved.
    # -----------------------------------------------------

    messages.success(
        request,
        (
            f"{hearing.case_number} "
            f"was marked as completed."
        )
    )

    return hearing_redirect()


# =========================================================
# POSTPONE / RESCHEDULE HEARING
# =========================================================
@role_required("admin", "official")
@require_POST
@transaction.atomic
def postpone_hearing(
    request,
    hearing_id
):

    hearing = get_object_or_404(
        Hearing.objects.select_for_update(),
        hearing_id=hearing_id,
    )

    complaint = get_object_or_404(
        Complaint.objects.select_for_update(),
        complaint_id=hearing.complaint_id,
    )

    # -----------------------------------------------------
    # Ownership
    # -----------------------------------------------------

    if not user_can_manage_complaint(
        request,
        complaint
    ):

        messages.error(
            request,
            (
                "You cannot reschedule this hearing "
                "because the complaint is assigned "
                "to another Admin or Barangay Official."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Completed / cancelled protection
    # -----------------------------------------------------

    if hearing.status in [
        "Completed",
        "Cancelled",
    ]:

        messages.error(
            request,
            (
                "A completed or cancelled hearing "
                "cannot be rescheduled."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # New values
    # -----------------------------------------------------

    new_date = request.POST.get(
        "hearing_date",
        "",
    ).strip()

    new_start_time = request.POST.get(
        "start_time",
        "",
    ).strip()

    new_end_time = request.POST.get(
        "end_time",
        "",
    ).strip()

    new_chamber = request.POST.get(
        "chamber",
        "",
    ).strip()

    # -----------------------------------------------------
    # Date required
    # -----------------------------------------------------

    if not new_date:

        messages.error(
            request,
            "Please select a new hearing date."
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Parse date
    # -----------------------------------------------------

    try:

        parsed_date = datetime.strptime(
            new_date,
            "%Y-%m-%d",
        ).date()

    except ValueError:

        messages.error(
            request,
            "Invalid hearing date."
        )

        return hearing_redirect()

    if parsed_date < timezone.localdate():

        messages.error(
            request,
            (
                "The new hearing date "
                "cannot be in the past."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Start/end time
    #
    # If the form does not provide them,
    # retain the existing times.
    # -----------------------------------------------------

    parsed_start = hearing.start_time
    parsed_end = hearing.end_time

    if new_start_time:

        try:

            parsed_start = datetime.strptime(
                new_start_time,
                "%H:%M",
            ).time()

        except ValueError:

            messages.error(
                request,
                "Invalid start time."
            )

            return hearing_redirect()

    if new_end_time:

        try:

            parsed_end = datetime.strptime(
                new_end_time,
                "%H:%M",
            ).time()

        except ValueError:

            messages.error(
                request,
                "Invalid end time."
            )

            return hearing_redirect()

    if parsed_end <= parsed_start:

        messages.error(
            request,
            (
                "End time must be later "
                "than start time."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Chamber
    # -----------------------------------------------------

    chamber = (
        new_chamber
        or
        hearing.chamber
    )

    # -----------------------------------------------------
    # Check chamber conflict
    # -----------------------------------------------------

    conflict = (
        Hearing.objects
        .filter(
            hearing_date=
                parsed_date,

            chamber=
                chamber,

            status__in=[
                "Scheduled",
                "In Progress",
                "Postponed",
            ],

            start_time__lt=
                parsed_end,

            end_time__gt=
                parsed_start,
        )
        .exclude(
            hearing_id=
                hearing.hearing_id
        )
        .exists()
    )

    if conflict:

        messages.error(
            request,
            (
                "The selected chamber already "
                "has another hearing during "
                "that time."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Reschedule
    #
    # Once a new date is supplied it becomes Scheduled
    # again rather than remaining Postponed.
    # -----------------------------------------------------

    hearing.hearing_date = parsed_date
    hearing.start_time = parsed_start
    hearing.end_time = parsed_end
    hearing.chamber = chamber
    hearing.status = "Scheduled"

    hearing.save(
        update_fields=[
            "hearing_date",
            "start_time",
            "end_time",
            "chamber",
            "status",
        ]
    )

    # -----------------------------------------------------
    # Complaint returns to Hearing Scheduled
    # -----------------------------------------------------

    complaint.status = "Hearing Scheduled"
    complaint.updated_at = timezone.now()

    complaint.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    messages.success(
        request,
        (
            f"{hearing.case_number} "
            f"was rescheduled successfully."
        )
    )

    return hearing_redirect()


# =========================================================
# CANCEL HEARING
# =========================================================
@role_required("admin", "official")
@require_POST
@transaction.atomic
def cancel_hearing(
    request,
    hearing_id
):

    hearing = get_object_or_404(
        Hearing.objects.select_for_update(),
        hearing_id=hearing_id,
    )

    complaint = get_object_or_404(
        Complaint.objects.select_for_update(),
        complaint_id=hearing.complaint_id,
    )

    # -----------------------------------------------------
    # Ownership
    # -----------------------------------------------------

    if not user_can_manage_complaint(
        request,
        complaint
    ):

        messages.error(
            request,
            (
                "You cannot cancel this hearing "
                "because the complaint is assigned "
                "to another Admin or Barangay Official."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Completed hearing
    # -----------------------------------------------------

    if hearing.status == "Completed":

        messages.error(
            request,
            (
                "A completed hearing "
                "cannot be cancelled."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Already cancelled
    # -----------------------------------------------------

    if hearing.status == "Cancelled":

        messages.info(
            request,
            "This hearing is already cancelled."
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Cancel
    # -----------------------------------------------------

    hearing.status = "Cancelled"

    hearing.save(
        update_fields=[
            "status",
        ]
    )

    # -----------------------------------------------------
    # If complaint was already placed into Under Mediation
    # because the hearing started, return it to the hearing
    # scheduling stage.
    # -----------------------------------------------------

    if complaint.status == "Under Mediation":

        complaint.status = "Hearing Scheduled"
        complaint.updated_at = timezone.now()

        complaint.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    messages.success(
        request,
        (
            f"{hearing.case_number} "
            f"was cancelled."
        )
    )

    return hearing_redirect()


# =========================================================
# SAVE HEARING NOTES
# =========================================================
@role_required("admin", "official")
@require_POST
@transaction.atomic
def save_hearing_notes(
    request,
    hearing_id
):

    hearing = get_object_or_404(
        Hearing.objects.select_for_update(),
        hearing_id=hearing_id,
    )

    complaint = get_object_or_404(
        Complaint,
        complaint_id=hearing.complaint_id,
    )

    # -----------------------------------------------------
    # Ownership
    # -----------------------------------------------------

    if not user_can_manage_complaint(
        request,
        complaint
    ):

        messages.error(
            request,
            (
                "You cannot modify the notes "
                "for another official's hearing."
            )
        )

        return hearing_redirect()

       # -----------------------------------------------------
    # Notes can only be edited while hearing is active
    # -----------------------------------------------------

    if hearing.status != "In Progress":

        messages.error(
            request,
            (
                "Hearing notes can only be edited "
                "while the hearing is in progress."
            )
        )

        return hearing_redirect()
    # -----------------------------------------------------
    # Notes
    # -----------------------------------------------------

    notes = request.POST.get(
        "notes",
        "",
    ).strip()

    hearing.notes = (
        notes
        or
        None
    )

    hearing.save(
        update_fields=[
            "notes",
        ]
    )

    messages.success(
        request,
        "Hearing notes were saved."
    )

    return hearing_redirect()


# =========================================================
# UPLOAD HEARING ATTACHMENT
# =========================================================
@role_required("admin", "official")
@require_POST
def upload_hearing_attachment(
    request,
    hearing_id
):

    hearing = get_object_or_404(
        Hearing,
        hearing_id=hearing_id,
    )

    complaint = get_object_or_404(
        Complaint,
        complaint_id=hearing.complaint_id,
    )

    # -----------------------------------------------------
    # Ownership
    # -----------------------------------------------------

    if not user_can_manage_complaint(
        request,
        complaint
    ):

        messages.error(
            request,
            (
                "You cannot upload files "
                "to another official's hearing."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Hearing status
    #
    # Allow upload during hearing and after completion.
    # -----------------------------------------------------

    if hearing.status not in [
        "In Progress",
        "Completed",
    ]:

        messages.error(
            request,
            (
                "Voice recordings and documents "
                "can only be uploaded during "
                "or after the hearing."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # User
    # -----------------------------------------------------

    current_user_id = (
        get_current_user_id(
            request
        )
    )

    if not current_user_id:

        messages.error(
            request,
            "Your login session has expired."
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # File
    # -----------------------------------------------------

    uploaded_file = (
        request.FILES.get(
            "file"
        )
    )

    if not uploaded_file:

        messages.error(
            request,
            "Please select a file."
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Size
    # -----------------------------------------------------

    if (
        uploaded_file.size
        >
        MAX_ATTACHMENT_SIZE
    ):

        messages.error(
            request,
            (
                "The maximum allowed "
                "file size is 25 MB."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Extension
    # -----------------------------------------------------

    filename = (
        uploaded_file.name
        or
        ""
    )

    extension = (
        Path(
            filename
        )
        .suffix
        .lower()
    )

    if (
        extension
        not in
        ALLOWED_ATTACHMENT_EXTENSIONS
    ):

        messages.error(
            request,
            (
                "Unsupported file type. "
                "Allowed files include images, "
                "audio recordings, PDF, DOC, "
                "DOCX, and TXT."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Attachment type
    # -----------------------------------------------------

    attachment_type = (
        request.POST.get(
            "attachment_type",
            "Document",
        )
        .strip()
    )

    allowed_attachment_types = [
        choice[0]

        for choice
        in HearingAttachment
        .ATTACHMENT_TYPE_CHOICES
    ]

    if (
        attachment_type
        not in
        allowed_attachment_types
    ):

        attachment_type = "Document"

    # -----------------------------------------------------
    # Automatically classify audio when necessary
    # -----------------------------------------------------

    audio_extensions = {
        ".mp3",
        ".wav",
        ".ogg",
        ".m4a",
        ".aac",
    }

    image_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
    }

    if extension in audio_extensions:

        attachment_type = (
            "Audio Recording"
        )

    elif (
        extension in image_extensions
        and
        attachment_type == "Document"
    ):

        attachment_type = "Image"

    # -----------------------------------------------------
    # Description
    # -----------------------------------------------------

    description = (
        request.POST.get(
            "description",
            "",
        )
        .strip()
        or
        None
    )

    # -----------------------------------------------------
    # Create attachment
    # -----------------------------------------------------

    HearingAttachment.objects.create(

        hearing=
            hearing,

        attachment_type=
            attachment_type,

        file=
            uploaded_file,

        original_filename=
            filename,

        file_type=(
            uploaded_file.content_type
            or
            ""
        ),

        file_size=
            uploaded_file.size,

        uploaded_by=
            current_user_id,

        description=
            description,
    )

    messages.success(
        request,
        (
            f"{filename} was uploaded "
            f"to {hearing.case_number}."
        )
    )

    return hearing_redirect()


# =========================================================
# DELETE HEARING ATTACHMENT
# =========================================================
@role_required("admin", "official")
@require_POST
@transaction.atomic
def delete_hearing_attachment(
    request,
    attachment_id
):

    attachment = get_object_or_404(
        HearingAttachment,
        attachment_id=attachment_id,
    )

    hearing = attachment.hearing

    complaint = get_object_or_404(
        Complaint,
        complaint_id=hearing.complaint_id,
    )

    # -----------------------------------------------------
    # Ownership
    # -----------------------------------------------------

    if not user_can_manage_complaint(
        request,
        complaint
    ):

        messages.error(
            request,
            (
                "You cannot remove files "
                "from another official's hearing."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Delete physical file
    # -----------------------------------------------------

    if attachment.file:

        attachment.file.delete(
            save=False
        )

    # -----------------------------------------------------
    # Delete DB record
    # -----------------------------------------------------

    attachment.delete()

    messages.success(
        request,
        "Hearing file was removed."
    )

    return hearing_redirect()


# =========================================================
# GENERATE OFFICIAL HEARING MINUTES
# =========================================================

@role_required("admin", "official")
@require_POST
def generate_hearing_minutes(
    request,
    hearing_id
):

    # -----------------------------------------------------
    # Hearing
    # -----------------------------------------------------

    hearing = get_object_or_404(
        Hearing,
        hearing_id=hearing_id,
    )

    # -----------------------------------------------------
    # Complaint
    # -----------------------------------------------------

    complaint = get_object_or_404(
        Complaint,
        complaint_id=hearing.complaint_id,
    )

    # -----------------------------------------------------
    # Ownership
    # -----------------------------------------------------

    if not user_can_manage_complaint(
        request,
        complaint
    ):

        messages.error(
            request,
            (
                "You cannot generate the Hearing Minutes "
                "for another official's hearing."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Hearing must be completed
    # -----------------------------------------------------

    if hearing.status != "Completed":

        messages.error(
            request,
            (
                "Official Hearing Minutes can only be "
                "generated after the hearing is completed."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Hearing notes are required
    # -----------------------------------------------------

    if not hearing.notes or not hearing.notes.strip():

        messages.error(
            request,
            (
                "Hearing Minutes cannot be generated "
                "because no hearing notes were recorded."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Current user
    # -----------------------------------------------------

    current_user_id = get_current_user_id(
        request
    )

    if not current_user_id:

        messages.error(
            request,
            "Your login session has expired."
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # User record
    # -----------------------------------------------------

    try:

        current_user = User.objects.get(
            user_id=current_user_id
        )

    except User.DoesNotExist:

        messages.error(
            request,
            (
                "The account that is processing this "
                "document could not be found."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Existing Hearing Minutes document
    # -----------------------------------------------------

    existing_document = (
        HearingMinutesDocument.objects
        .filter(
            hearing_id=hearing.hearing_id,
            document_type="HEARING_MINUTES",
        )
        .first()
    )

    # Once registered on Fabric, the PDF must not
    # be regenerated or overwritten because that would
    # produce a different SHA-256 hash.

    if (
        existing_document
        and
        existing_document.blockchain_status == "Registered"
    ):

        messages.error(
            request,
            (
                "The official Hearing Minutes have already "
                "been registered on the blockchain and "
                "cannot be regenerated."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Generate PDF
    # -----------------------------------------------------

    try:

        hearing_document = (
            generate_hearing_minutes_pdf(
                hearing_id=hearing.hearing_id,
                processed_by=current_user.user_id,
                processed_by_name=current_user.username,
                processed_by_role=current_user.role,
            )
        )

    except ValueError as error:

        messages.error(
            request,
            str(error)
        )

        return hearing_redirect()

    except Exception:

        messages.error(
            request,
            (
                "The official Hearing Minutes could not "
                "be generated. Please try again."
            )
        )

        return hearing_redirect()

    # -----------------------------------------------------
    # Success
    # -----------------------------------------------------

    messages.success(
        request,
        (
            f"Official Hearing Minutes "
            f"{hearing_document.file_name} "
            f"were generated successfully."
        )
    )

    return hearing_redirect()