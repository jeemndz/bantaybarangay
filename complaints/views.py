from datetime import timedelta
from pathlib import Path

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db import transaction

from .models import Complaint
from residentmodule.models import Resident
from evidencemodule.views import save_evidence_file
from usermanagement.models import User


# =========================================================
# CONSTANTS
# =========================================================

ALLOWED_COMPLAINT_STATUSES = [
    "Submitted",
    "Under Review",
    "Summons Issued",
    "Hearing Scheduled",
    "Under Mediation",
    "For Verification",
    "Settled",
    "For Document Released",
    "Referred",
    "Resolved",
    "Rejected",
    "Closed",
]


ALLOWED_COMPLAINT_PRIORITIES = [
    "N/A",
    "Low",
    "Medium",
    "High",
    "Urgent",
]


ALLOWED_REPORT_TYPES = [
    "Formal Complaint",
    "Community Issue",
]


ALLOWED_CASE_HANDLER_ROLES = [
    "admin",
    "official",
]


COMPLAINTS_PER_PAGE = 10


# =========================================================
# EVIDENCE SETTINGS
# =========================================================

MAX_EVIDENCE_FILES = 5

MAX_EVIDENCE_FILE_SIZE = (
    10 * 1024 * 1024
)


ALLOWED_EVIDENCE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",

    ".mp4",
    ".webm",
    ".mov",

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


# =========================================================
# GET LOGGED-IN STAFF USER
# =========================================================

def get_logged_in_staff_user(request):

    user_id = request.session.get(
        "user_id"
    )


    if not user_id:

        return None


    return (
        User.objects
        .filter(
            user_id=user_id,
            role__in=ALLOWED_CASE_HANDLER_ROLES,
            is_active=True,
        )
        .first()
    )


# =========================================================
# RESIDENT FIELD HELPER
# =========================================================

def get_resident_field(
    resident,
    *field_names
):

    for field_name in field_names:

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


    return ""


# =========================================================
# RESIDENT FULL NAME
# =========================================================

def get_resident_full_name(
    resident
):

    if not resident:

        return "Unknown Resident"


    full_name = get_resident_field(
        resident,
        "full_name",
        "fullname",
        "resident_name",
        "name",
    )


    if full_name:

        return full_name


    first_name = get_resident_field(
        resident,
        "first_name",
        "firstname",
        "given_name",
    )


    middle_name = get_resident_field(
        resident,
        "middle_name",
        "middlename",
        "middle_initial",
    )


    last_name = get_resident_field(
        resident,
        "last_name",
        "lastname",
        "surname",
    )


    suffix = get_resident_field(
        resident,
        "suffix",
        "suffix_name",
        "name_suffix",
    )


    name_parts = [
        first_name,
        middle_name,
        last_name,
        suffix,
    ]


    full_name = " ".join(
        part
        for part in name_parts
        if part
    ).strip()


    if full_name:

        return full_name


    resident_id = getattr(
        resident,
        "resident_id",
        None
    )


    if resident_id:

        return (
            f"Resident #{resident_id}"
        )


    return "Unknown Resident"


# =========================================================
# ATTACH RESIDENT NAMES
# =========================================================

def attach_resident_names(
    complaints
):

    complaint_list = list(
        complaints
    )


    if not complaint_list:

        return complaint_list


    resident_ids = {

        complaint.resident_id

        for complaint in complaint_list

        if complaint.resident_id
    }


    residents = (
        Resident.objects
        .filter(
            resident_id__in=resident_ids
        )
    )


    resident_map = {

        resident.resident_id:
            resident

        for resident in residents
    }


    for complaint in complaint_list:

        resident = resident_map.get(
            complaint.resident_id
        )


        if resident:

            complaint.resident = resident

            complaint.resident_name = (
                get_resident_full_name(
                    resident
                )
            )

        else:

            complaint.resident = None

            complaint.resident_name = (
                f"Resident #{complaint.resident_id}"
                if complaint.resident_id
                else "Unknown Resident"
            )


    return complaint_list


# =========================================================
# ATTACH ASSIGNED USER INFORMATION
# =========================================================

def attach_assignment_information(
    complaints,
    logged_in_user
):

    complaint_list = list(
        complaints
    )


    assigned_ids = {

        complaint.assigned_official

        for complaint in complaint_list

        if complaint.assigned_official
    }


    assigned_users = (
        User.objects
        .filter(
            user_id__in=assigned_ids
        )
    )


    user_map = {

        user.user_id:
            user

        for user in assigned_users
    }


    for complaint in complaint_list:

        assigned_user = (
            user_map.get(
                complaint.assigned_official
            )
        )


        if assigned_user:

            complaint.assigned_username = (
                assigned_user.username
            )


            complaint.assigned_role = (
                assigned_user.role
            )

        else:

            complaint.assigned_username = ""
            complaint.assigned_role = ""


        # -------------------------------------------------
        # EDITING PERMISSION
        # -------------------------------------------------
        #
        # Unassigned complaints:
        # Any valid Admin / Official may review.
        #
        # Assigned complaints:
        # Only the assigned account may edit.
        # -------------------------------------------------

        if not logged_in_user:

            complaint.can_edit = False


        elif not complaint.assigned_official:

            complaint.can_edit = True


        else:

            complaint.can_edit = (
                complaint.assigned_official
                ==
                logged_in_user.user_id
            )


    return complaint_list


# =========================================================
# VALIDATE EVIDENCE
# =========================================================

def validate_evidence_files(
    evidence_files
):

    if (
        len(evidence_files)
        > MAX_EVIDENCE_FILES
    ):

        return (
            f"You may upload a maximum of "
            f"{MAX_EVIDENCE_FILES} evidence files."
        )


    for uploaded_file in evidence_files:

        if uploaded_file.size <= 0:

            return (
                f"{uploaded_file.name} is empty."
            )


        if (
            uploaded_file.size
            > MAX_EVIDENCE_FILE_SIZE
        ):

            return (
                f"{uploaded_file.name} exceeds "
                "the 10 MB file size limit."
            )


        extension = (
            Path(
                uploaded_file.name
            )
            .suffix
            .lower()
        )


        if (
            extension
            not in ALLOWED_EVIDENCE_EXTENSIONS
        ):

            return (
                f"{uploaded_file.name} is not "
                "a supported evidence file type."
            )


    return None


# =========================================================
# GET EVIDENCE UPLOADER
# =========================================================

def get_evidence_uploader(
    request,
    complaint=None,
    resident=None
):

    session_user_id = (
        request.session.get(
            "user_id"
        )
    )


    if session_user_id:

        return session_user_id


    if resident:

        resident_user_id = getattr(
            resident,
            "user_id",
            None
        )


        if resident_user_id:

            return resident_user_id


    if complaint:

        try:

            complaint_resident = (
                Resident.objects.get(
                    resident_id=(
                        complaint.resident_id
                    )
                )
            )


            resident_user_id = getattr(
                complaint_resident,
                "user_id",
                None
            )


            if resident_user_id:

                return resident_user_id


        except Resident.DoesNotExist:

            pass


    return None


# =========================================================
# SAVE EVIDENCE
# =========================================================

def save_complaint_evidence(
    evidence_files,
    complaint,
    uploaded_by
):

    evidence_saved = 0
    evidence_failed = 0


    if not evidence_files:

        return (
            evidence_saved,
            evidence_failed,
        )


    if not uploaded_by:

        return (
            0,
            len(evidence_files),
        )


    for uploaded_file in evidence_files:

        try:

            save_evidence_file(

                uploaded_file=(
                    uploaded_file
                ),

                complaint_id=(
                    complaint.complaint_id
                ),

                uploaded_by=(
                    uploaded_by
                ),
            )


            evidence_saved += 1


        except Exception as error:

            evidence_failed += 1

            print(
                "EVIDENCE SAVE ERROR:",
                error
            )


    return (
        evidence_saved,
        evidence_failed,
    )


# =========================================================
# COMPLAINT MANAGEMENT
# =========================================================

def complaints(request):

    logged_in_user = (
        get_logged_in_staff_user(
            request
        )
    )


    all_complaints = (
        Complaint.objects
        .all()
        .order_by(
            "-submitted_at"
        )
    )


    # =====================================================
    # FILTERS
    # =====================================================

    category = request.GET.get(
        "category",
        ""
    ).strip()


    status = request.GET.get(
        "status",
        ""
    ).strip()


    date_range = request.GET.get(
        "date_range",
        ""
    ).strip()


    complaints_list = (
        all_complaints
    )


    if category:

        complaints_list = (
            complaints_list.filter(
                complaint_type=category
            )
        )


    if status:

        complaints_list = (
            complaints_list.filter(
                status=status
            )
        )


    if date_range == "30":

        thirty_days_ago = (
            timezone.now()
            -
            timedelta(
                days=30
            )
        )


        complaints_list = (
            complaints_list.filter(
                submitted_at__gte=(
                    thirty_days_ago
                )
            )
        )


    # =====================================================
    # SECTIONS
    # =====================================================

    new_complaints_queryset = (
        complaints_list.filter(
            status__in=[
                "Submitted",
                "Under Review",
            ]
        )
    )


    ongoing_complaints_queryset = (
        complaints_list.filter(
            status__in=[
                "Summons Issued",
                "Hearing Scheduled",
                "Under Mediation",
                "For Verification",
                "Settled",
                "For Document Released",
                "Referred",
            ]
        )
    )


    completed_complaints_queryset = (
        complaints_list.filter(
            status__in=[
                "Resolved",
                "Rejected",
                "Closed",
            ]
        )
    )


    # =====================================================
    # PAGINATION
    # =====================================================

    new_paginator = Paginator(
        new_complaints_queryset,
        COMPLAINTS_PER_PAGE
    )


    new_page = (
        new_paginator.get_page(
            request.GET.get(
                "new_page",
                1
            )
        )
    )


    ongoing_paginator = Paginator(
        ongoing_complaints_queryset,
        COMPLAINTS_PER_PAGE
    )


    ongoing_page = (
        ongoing_paginator.get_page(
            request.GET.get(
                "ongoing_page",
                1
            )
        )
    )


    completed_paginator = Paginator(
        completed_complaints_queryset,
        COMPLAINTS_PER_PAGE
    )


    completed_page = (
        completed_paginator.get_page(
            request.GET.get(
                "completed_page",
                1
            )
        )
    )


    # =====================================================
    # ATTACH DISPLAY INFORMATION
    # =====================================================

    attach_resident_names(
        new_page.object_list
    )

    attach_resident_names(
        ongoing_page.object_list
    )

    attach_resident_names(
        completed_page.object_list
    )


    attach_assignment_information(
        new_page.object_list,
        logged_in_user
    )

    attach_assignment_information(
        ongoing_page.object_list,
        logged_in_user
    )

    attach_assignment_information(
        completed_page.object_list,
        logged_in_user
    )


    # =====================================================
    # STATISTICS
    # =====================================================

    total_complaints = (
        all_complaints.count()
    )


    pending_complaints = (
        all_complaints
        .filter(
            status__in=[
                "Submitted",
                "Under Review",
            ]
        )
        .count()
    )


    ongoing_count = (
        all_complaints
        .filter(
            status__in=[
                "Summons Issued",
                "Hearing Scheduled",
                "Under Mediation",
                "For Verification",
                "Settled",
                "For Document Released",
                "Referred",
            ]
        )
        .count()
    )


    resolved_complaints = (
        all_complaints
        .filter(
            status="Resolved"
        )
        .count()
    )


    completed_count = (
        all_complaints
        .filter(
            status__in=[
                "Resolved",
                "Rejected",
                "Closed",
            ]
        )
        .count()
    )


    if total_complaints > 0:

        resolved_percentage = round(
            (
                resolved_complaints
                /
                total_complaints
            )
            * 100
        )

    else:

        resolved_percentage = 0


    # =====================================================
    # AVERAGE CLOSE TIME
    # =====================================================

    completed_for_average = (
        all_complaints.filter(
            status__in=[
                "Resolved",
                "Closed",
            ]
        )
    )


    total_close_days = 0
    close_count = 0


    for complaint in completed_for_average:

        if (
            complaint.submitted_at
            and
            complaint.updated_at
        ):

            difference = (
                complaint.updated_at
                -
                complaint.submitted_at
            )


            total_close_days += max(
                difference.days,
                0
            )

            close_count += 1


    if close_count:

        average_close_days = round(
            total_close_days
            /
            close_count,
            1
        )

    else:

        average_close_days = 0


    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        "complaints":
            complaints_list,

        "new_complaints":
            new_page,

        "ongoing_complaints":
            ongoing_page,

        "completed_complaints":
            completed_page,

        "new_page":
            new_page,

        "ongoing_page":
            ongoing_page,

        "completed_page":
            completed_page,

        "total_complaints":
            total_complaints,

        "pending_complaints":
            pending_complaints,

        "ongoing_count":
            ongoing_count,

        "completed_count":
            completed_count,

        "resolved_percentage":
            resolved_percentage,

        "average_close_days":
            average_close_days,

        "selected_category":
            category,

        "selected_status":
            status,

        "selected_date_range":
            date_range,

        "logged_in_user":
            logged_in_user,
    }


    return render(
        request,
        "complaintmodule/complaints.html",
        context
    )


# =========================================================
# UPDATE COMPLAINT
# =========================================================

@require_POST
def update_complaint(
    request,
    complaint_id
):

    # =====================================================
    # CURRENT STAFF USER
    # =====================================================

    logged_in_user = (
        get_logged_in_staff_user(
            request
        )
    )


    if not logged_in_user:

        messages.error(
            request,
            (
                "Only an active Administrator or "
                "Barangay Official may process complaints."
            )
        )

        return redirect(
            "complaints"
        )


    # =====================================================
    # GET FORM VALUES
    # =====================================================

    priority = request.POST.get(
        "priority",
        ""
    ).strip()


    new_status = request.POST.get(
        "status",
        ""
    ).strip()


    resolution = request.POST.get(
        "resolution",
        ""
    ).strip()


    evidence_files = (
        request.FILES.getlist(
            "evidence"
        )
    )


    # =====================================================
    # BASIC VALIDATION
    # =====================================================

    if (
        priority
        not in ALLOWED_COMPLAINT_PRIORITIES
    ):

        messages.error(
            request,
            "Invalid complaint priority."
        )

        return redirect(
            "complaints"
        )


    if (
        new_status
        not in ALLOWED_COMPLAINT_STATUSES
    ):

        messages.error(
            request,
            "Invalid complaint status."
        )

        return redirect(
            "complaints"
        )


    evidence_error = (
        validate_evidence_files(
            evidence_files
        )
    )


    if evidence_error:

        messages.error(
            request,
            evidence_error
        )

        return redirect(
            "complaints"
        )


    # =====================================================
    # DATABASE-LEVEL OWNERSHIP CHECK
    # =====================================================

    newly_assigned = False


    with transaction.atomic():

        complaint = (
            Complaint.objects
            .select_for_update()
            .filter(
                complaint_id=complaint_id
            )
            .first()
        )


        if not complaint:

            messages.error(
                request,
                "Complaint not found."
            )

            return redirect(
                "complaints"
            )


        # =================================================
        # ALREADY ASSIGNED
        # =================================================

        if complaint.assigned_official:

            if (
                complaint.assigned_official
                !=
                logged_in_user.user_id
            ):

                messages.error(
                    request,
                    (
                        f"Complaint #CP-"
                        f"{complaint.complaint_id:04d} "
                        "is assigned to another Admin or "
                        "Barangay Official. You may view it, "
                        "but you cannot modify it."
                    )
                )

                return redirect(
                    "complaints"
                )


        # =================================================
        # NEWLY SUBMITTED / UNASSIGNED
        # =================================================

        else:

            # ---------------------------------------------
            # CLAIM ONLY WHEN:
            #
            # Current DB status = Submitted
            # Requested status = Under Review
            # ---------------------------------------------

            if (
                complaint.status == "Submitted"
                and
                new_status == "Under Review"
            ):

                complaint.assigned_official = (
                    logged_in_user.user_id
                )

                newly_assigned = True


            # ---------------------------------------------
            # UNASSIGNED COMPLAINT CANNOT SKIP
            # UNDER REVIEW
            # ---------------------------------------------

            elif (
                complaint.status == "Submitted"
                and
                new_status != "Submitted"
            ):

                messages.error(
                    request,
                    (
                        "A newly submitted complaint must "
                        "first be changed to Under Review."
                    )
                )

                return redirect(
                    "complaints"
                )


        # =================================================
        # SAVE COMPLAINT DETAILS
        # =================================================

        complaint.priority = (
            priority
        )


        complaint.status = (
            new_status
        )


        complaint.resolution = (
            resolution
            if resolution
            else None
        )


        complaint.updated_at = (
            timezone.now()
        )


        update_fields = [
            "priority",
            "status",
            "resolution",
            "updated_at",
        ]


        if newly_assigned:

            update_fields.append(
                "assigned_official"
            )


        complaint.save(
            update_fields=update_fields
        )


    # =====================================================
    # SAVE EVIDENCE
    # =====================================================

    evidence_saved = 0
    evidence_failed = 0


    if evidence_files:

        (
            evidence_saved,
            evidence_failed,
        ) = save_complaint_evidence(

            evidence_files=(
                evidence_files
            ),

            complaint=(
                complaint
            ),

            uploaded_by=(
                logged_in_user.user_id
            ),
        )


    # =====================================================
    # MESSAGE
    # =====================================================

    if newly_assigned:

        if logged_in_user.role == "admin":

            role_name = (
                "Administrator"
            )

        else:

            role_name = (
                "Barangay Official"
            )


        messages.success(
            request,
            (
                f"Complaint #CP-"
                f"{complaint.complaint_id:04d} "
                "is now Under Review and has been "
                f"assigned to {logged_in_user.username} "
                f"({role_name})."
            )
        )


    elif (
        evidence_saved > 0
        and
        evidence_failed == 0
    ):

        messages.success(
            request,
            (
                f"Complaint #CP-"
                f"{complaint.complaint_id:04d} "
                "was updated successfully with "
                f"{evidence_saved} evidence file"
                f"{'s' if evidence_saved != 1 else ''}."
            )
        )


    elif evidence_failed > 0:

        messages.warning(
            request,
            (
                f"Complaint #CP-"
                f"{complaint.complaint_id:04d} "
                "was updated, but "
                f"{evidence_failed} evidence file"
                f"{'s' if evidence_failed != 1 else ''} "
                "could not be uploaded."
            )
        )


    else:

        messages.success(
            request,
            (
                f"Complaint #CP-"
                f"{complaint.complaint_id:04d} "
                "was updated successfully."
            )
        )


    return redirect(
        "complaints"
    )


# =========================================================
# NEW COMPLAINT
# =========================================================

def new_complaint(request):

    residents = (
        Resident.objects
        .all()
        .order_by(
            "resident_id"
        )
    )


    if request.method == "POST":

        resident_id = (
            request.POST.get(
                "resident_id"
            )
        )


        report_type = (
            request.POST.get(
                "report_type",
                "Formal Complaint"
            )
            .strip()
        )


        complaint_type = (
            request.POST.get(
                "complaint_type",
                ""
            )
            .strip()
        )


        subject = (
            request.POST.get(
                "subject",
                ""
            )
            .strip()
        )


        description = (
            request.POST.get(
                "description",
                ""
            )
            .strip()
        )


        location = (
            request.POST.get(
                "location",
                ""
            )
            .strip()
        )


        incident_date = (
            request.POST.get(
                "incident_date",
                ""
            )
            .strip()
        )


        incident_time = (
            request.POST.get(
                "incident_time",
                ""
            )
            .strip()
        )


        respondent_name = (
            request.POST.get(
                "respondent_name",
                ""
            )
            .strip()
        )


        respondent_address = (
            request.POST.get(
                "respondent_address",
                ""
            )
            .strip()
        )


        respondent_relationship = (
            request.POST.get(
                "respondent_relationship",
                ""
            )
            .strip()
        )


        respondent_contact = (
            request.POST.get(
                "respondent_contact",
                ""
            )
            .strip()
        )


        evidence_files = (
            request.FILES.getlist(
                "evidence"
            )
        )


        # =================================================
        # VALIDATION
        # =================================================

        if not resident_id:

            messages.error(
                request,
                "Please select a resident."
            )

            return render(
                request,
                "complaintmodule/newcomplaint.html",
                {
                    "residents":
                        residents,
                }
            )


        resident = get_object_or_404(
            Resident,
            resident_id=resident_id
        )


        if not complaint_type:

            messages.error(
                request,
                "Complaint type is required."
            )

            return render(
                request,
                "complaintmodule/newcomplaint.html",
                {
                    "residents":
                        residents,
                }
            )


        if not subject:

            messages.error(
                request,
                "Complaint subject is required."
            )

            return render(
                request,
                "complaintmodule/newcomplaint.html",
                {
                    "residents":
                        residents,
                }
            )


        if not description:

            messages.error(
                request,
                "Complaint description is required."
            )

            return render(
                request,
                "complaintmodule/newcomplaint.html",
                {
                    "residents":
                        residents,
                }
            )


        if (
            report_type
            not in ALLOWED_REPORT_TYPES
        ):

            report_type = (
                "Formal Complaint"
            )


        if (
            report_type
            ==
            "Community Issue"
        ):

            respondent_name = None
            respondent_address = None
            respondent_relationship = None
            respondent_contact = None


        evidence_error = (
            validate_evidence_files(
                evidence_files
            )
        )


        if evidence_error:

            messages.error(
                request,
                evidence_error
            )

            return render(
                request,
                "complaintmodule/newcomplaint.html",
                {
                    "residents":
                        residents,
                }
            )


        # =================================================
        # CREATE
        # =================================================

        try:

            complaint = (
                Complaint.objects.create(

                    resident_id=(
                        resident.resident_id
                    ),

                    report_type=(
                        report_type
                    ),

                    complaint_type=(
                        complaint_type
                    ),

                    subject=(
                        subject
                    ),

                    description=(
                        description
                    ),

                    location=(
                        location
                        if location
                        else None
                    ),

                    incident_date=(
                        incident_date
                        if incident_date
                        else None
                    ),

                    incident_time=(
                        incident_time
                        if incident_time
                        else None
                    ),

                    respondent_name=(
                        respondent_name
                        if respondent_name
                        else None
                    ),

                    respondent_address=(
                        respondent_address
                        if respondent_address
                        else None
                    ),

                    respondent_relationship=(
                        respondent_relationship
                        if respondent_relationship
                        else None
                    ),

                    respondent_contact=(
                        respondent_contact
                        if respondent_contact
                        else None
                    ),

                    priority="N/A",

                    # IMPORTANT:
                    # NEW COMPLAINT STARTS UNASSIGNED
                    status="Submitted",

                    assigned_official=None,

                    resolution=None,

                    submitted_at=(
                        timezone.now()
                    ),

                    updated_at=(
                        timezone.now()
                    ),
                )
            )


        except Exception as error:

            print(
                "COMPLAINT CREATE ERROR:",
                error
            )


            messages.error(
                request,
                "The complaint could not be created."
            )

            return render(
                request,
                "complaintmodule/newcomplaint.html",
                {
                    "residents":
                        residents,
                }
            )


        # =================================================
        # EVIDENCE
        # =================================================

        uploaded_by = (
            get_evidence_uploader(
                request,
                complaint=complaint,
                resident=resident
            )
        )


        (
            evidence_saved,
            evidence_failed,
        ) = save_complaint_evidence(

            evidence_files=(
                evidence_files
            ),

            complaint=(
                complaint
            ),

            uploaded_by=(
                uploaded_by
            ),
        )


        if evidence_failed:

            messages.warning(
                request,
                (
                    f"Complaint #CP-"
                    f"{complaint.complaint_id:04d} "
                    "was created, but some evidence "
                    "files could not be uploaded."
                )
            )

        else:

            messages.success(
                request,
                (
                    f"Complaint #CP-"
                    f"{complaint.complaint_id:04d} "
                    "was submitted successfully."
                )
            )


        return redirect(
            "complaints"
        )


    return render(
        request,
        "complaintmodule/newcomplaint.html",
        {
            "residents":
                residents,
        }
    )