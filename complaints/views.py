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

from .models import Complaint
from residentmodule.models import Resident
from evidencemodule.views import save_evidence_file


# =========================================================
# CONSTANTS
# =========================================================

ALLOWED_COMPLAINT_STATUSES = [
    "Submitted",
    "Under Review",
    "Under Investigation",
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


# =========================================================
# PAGINATION SETTINGS
# =========================================================

COMPLAINTS_PER_PAGE = 10


# =========================================================
# EVIDENCE SETTINGS
# =========================================================

MAX_EVIDENCE_FILES = 5

MAX_EVIDENCE_FILE_SIZE = (
    10 * 1024 * 1024
)  # 10 MB


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
# RESIDENT NAME HELPERS
# =========================================================

def get_resident_field(
    resident,
    *field_names
):

    """
    Return the first available value from the supplied
    Resident model field names.

    This allows the complaint module to work with common
    Resident naming conventions such as:

        first_name
        firstname

        middle_name
        middlename

        last_name
        lastname

        suffix
        suffix_name
    """

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
# GET RESIDENT FULL NAME
# =========================================================

def get_resident_full_name(
    resident
):

    """
    Build the resident's display name.

    If the Resident model already has a full_name field
    or property, that value is used first.
    """

    if not resident:

        return "Unknown Resident"


    # =====================================================
    # EXISTING FULL NAME FIELD / PROPERTY
    # =====================================================

    full_name = get_resident_field(
        resident,
        "full_name",
        "fullname",
        "resident_name",
        "name",
    )


    if full_name:

        return full_name


    # =====================================================
    # INDIVIDUAL NAME PARTS
    # =====================================================

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


    # =====================================================
    # FALLBACK
    # =====================================================

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
# ATTACH RESIDENT NAMES TO COMPLAINTS
# =========================================================

def attach_resident_names(
    complaints
):

    """
    Attach a temporary resident_name attribute to every
    complaint object.

    The complaints table stores resident_id rather than
    a Django ForeignKey, so this avoids performing one
    Resident query for every complaint row.
    """

    complaint_list = list(
        complaints
    )


    if not complaint_list:

        return complaint_list


    # =====================================================
    # COLLECT RESIDENT IDS
    # =====================================================

    resident_ids = {

        complaint.resident_id

        for complaint in complaint_list

        if complaint.resident_id

    }


    if not resident_ids:

        for complaint in complaint_list:

            complaint.resident_name = (
                "Unknown Resident"
            )

        return complaint_list


    # =====================================================
    # LOAD RESIDENTS IN ONE QUERY
    # =====================================================

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


    # =====================================================
    # ATTACH RESIDENT INFORMATION
    # =====================================================

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
# VALIDATE EVIDENCE FILES
# =========================================================

def validate_evidence_files(
    evidence_files
):

    """
    Validate evidence uploaded either while creating a
    complaint or while reviewing an existing complaint.

    Returns:

        None
            when all files are valid.

        str
            when validation fails.
    """

    # =====================================================
    # MAXIMUM NUMBER OF FILES
    # =====================================================

    if (
        len(evidence_files)
        > MAX_EVIDENCE_FILES
    ):

        return (
            "You may upload a maximum "
            f"of {MAX_EVIDENCE_FILES} "
            "evidence files."
        )


    # =====================================================
    # VALIDATE EACH FILE
    # =====================================================

    for uploaded_file in evidence_files:

        # -------------------------------------------------
        # EMPTY FILE
        # -------------------------------------------------

        if (
            uploaded_file.size <= 0
        ):

            return (
                f"{uploaded_file.name} "
                "is empty and cannot be uploaded."
            )


        # -------------------------------------------------
        # FILE SIZE
        # -------------------------------------------------

        if (
            uploaded_file.size
            > MAX_EVIDENCE_FILE_SIZE
        ):

            return (
                f"{uploaded_file.name} "
                "exceeds the 10 MB "
                "file size limit."
            )


        # -------------------------------------------------
        # FILE EXTENSION
        # -------------------------------------------------

        file_extension = (
            Path(
                uploaded_file.name
            )
            .suffix
            .lower()
        )


        if (
            file_extension
            not in ALLOWED_EVIDENCE_EXTENSIONS
        ):

            return (
                f"{uploaded_file.name} "
                "is not a supported "
                "evidence file type."
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

    """
    Determine which user ID should be stored in the
    evidence.uploaded_by field.

    The logged-in session user is preferred.
    """

    session_user_id = (
        request.session.get(
            "user_id"
        )
    )


    if session_user_id:

        return session_user_id


    # =====================================================
    # RESIDENT USER ID
    # =====================================================

    if resident:

        resident_user_id = getattr(
            resident,
            "user_id",
            None
        )


        if resident_user_id:

            return resident_user_id


    # =====================================================
    # COMPLAINT RESIDENT
    # =====================================================

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
# SAVE MULTIPLE EVIDENCE FILES
# =========================================================

def save_complaint_evidence(
    evidence_files,
    complaint,
    uploaded_by
):

    """
    Save all supplied evidence files using the existing
    evidencemodule save_evidence_file() helper.

    Returns:

        evidence_saved
        evidence_failed
    """

    evidence_saved = 0
    evidence_failed = 0


    if not evidence_files:

        return (
            evidence_saved,
            evidence_failed,
        )


    if not uploaded_by:

        return (
            evidence_saved,
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

    # =====================================================
    # ALL COMPLAINTS
    # =====================================================

    all_complaints = (
        Complaint.objects
        .all()
        .order_by("-submitted_at")
    )


    # =====================================================
    # FILTER VALUES
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


    # =====================================================
    # FILTERED QUERYSET
    # =====================================================

    complaints_list = (
        all_complaints
    )


    # -----------------------------------------------------
    # CATEGORY FILTER
    # -----------------------------------------------------

    if category:

        complaints_list = (
            complaints_list.filter(
                complaint_type=category
            )
        )


    # -----------------------------------------------------
    # STATUS FILTER
    # -----------------------------------------------------

    if status:

        complaints_list = (
            complaints_list.filter(
                status=status
            )
        )


    # -----------------------------------------------------
    # LAST 30 DAYS
    # -----------------------------------------------------

    if date_range == "30":

        thirty_days_ago = (
            timezone.now()
            - timedelta(
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
    # SPLIT INTO THREE TABLES
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
            status=(
                "Under Investigation"
            )
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

    # -----------------------------------------------------
    # NEW COMPLAINTS
    # -----------------------------------------------------

    new_paginator = Paginator(
        new_complaints_queryset,
        COMPLAINTS_PER_PAGE
    )


    new_page_number = request.GET.get(
        "new_page",
        1
    )


    new_page = (
        new_paginator.get_page(
            new_page_number
        )
    )


    # -----------------------------------------------------
    # ONGOING COMPLAINTS
    # -----------------------------------------------------

    ongoing_paginator = Paginator(
        ongoing_complaints_queryset,
        COMPLAINTS_PER_PAGE
    )


    ongoing_page_number = (
        request.GET.get(
            "ongoing_page",
            1
        )
    )


    ongoing_page = (
        ongoing_paginator.get_page(
            ongoing_page_number
        )
    )


    # -----------------------------------------------------
    # COMPLETED COMPLAINTS
    # -----------------------------------------------------

    completed_paginator = Paginator(
        completed_complaints_queryset,
        COMPLAINTS_PER_PAGE
    )


    completed_page_number = (
        request.GET.get(
            "completed_page",
            1
        )
    )


    completed_page = (
        completed_paginator.get_page(
            completed_page_number
        )
    )


    # =====================================================
    # ATTACH RESIDENT NAMES
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


    # =====================================================
    # STATISTICS
    # =====================================================

    total_complaints = (
        all_complaints.count()
    )


    pending_complaints = (
        all_complaints.filter(
            status__in=[
                "Submitted",
                "Under Review",
                "Under Investigation",
            ]
        ).count()
    )


    ongoing_count = (
        all_complaints.filter(
            status=(
                "Under Investigation"
            )
        ).count()
    )


    resolved_complaints = (
        all_complaints.filter(
            status="Resolved"
        ).count()
    )


    completed_count = (
        all_complaints.filter(
            status__in=[
                "Resolved",
                "Rejected",
                "Closed",
            ]
        ).count()
    )


    # =====================================================
    # RESOLVED PERCENTAGE
    # =====================================================

    if total_complaints > 0:

        resolved_percentage = round(
            (
                resolved_complaints
                /
                total_complaints
            )
            *
            100
        )

    else:

        resolved_percentage = 0


    # =====================================================
    # AVERAGE TIME TO CLOSE
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


    if close_count > 0:

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

        # -------------------------------------------------
        # FILTERED COMPLAINTS
        # -------------------------------------------------

        "complaints":
            complaints_list,


        # -------------------------------------------------
        # PAGINATED TABLE DATA
        # -------------------------------------------------

        "new_complaints":
            new_page,

        "ongoing_complaints":
            ongoing_page,

        "completed_complaints":
            completed_page,


        # -------------------------------------------------
        # PAGE OBJECTS
        # -------------------------------------------------

        "new_page":
            new_page,

        "ongoing_page":
            ongoing_page,

        "completed_page":
            completed_page,


        # -------------------------------------------------
        # COUNTS
        # -------------------------------------------------

        "total_complaints":
            total_complaints,

        "pending_complaints":
            pending_complaints,

        "ongoing_count":
            ongoing_count,

        "completed_count":
            completed_count,


        # -------------------------------------------------
        # STATISTICS
        # -------------------------------------------------

        "resolved_percentage":
            resolved_percentage,

        "average_close_days":
            average_close_days,


        # -------------------------------------------------
        # FILTER VALUES
        # -------------------------------------------------

        "selected_category":
            category,

        "selected_status":
            status,

        "selected_date_range":
            date_range,
    }


    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "complaintmodule/complaints.html",
        context
    )


# =========================================================
# UPDATE COMPLAINT REVIEW
# =========================================================

@require_POST
def update_complaint(
    request,
    complaint_id
):

    # =====================================================
    # GET COMPLAINT
    # =====================================================

    complaint = get_object_or_404(
        Complaint,
        complaint_id=complaint_id
    )


    # =====================================================
    # GET FORM VALUES
    # =====================================================

    priority = request.POST.get(
        "priority",
        ""
    ).strip()


    status = request.POST.get(
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
    # VALIDATE PRIORITY
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


    # =====================================================
    # VALIDATE STATUS
    # =====================================================

    if (
        status
        not in ALLOWED_COMPLAINT_STATUSES
    ):

        messages.error(
            request,
            "Invalid complaint status."
        )

        return redirect(
            "complaints"
        )


    # =====================================================
    # VALIDATE NEW EVIDENCE
    # =====================================================

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
    # UPDATE COMPLAINT
    # =====================================================

    complaint.priority = (
        priority
    )

    complaint.status = (
        status
    )

    complaint.resolution = (
        resolution
        if resolution
        else None
    )

    complaint.updated_at = (
        timezone.now()
    )


    complaint.save(
        update_fields=[
            "priority",
            "status",
            "resolution",
            "updated_at",
        ]
    )


    # =====================================================
    # SAVE NEW EVIDENCE
    # =====================================================

    evidence_saved = 0
    evidence_failed = 0


    if evidence_files:

        uploaded_by = (
            get_evidence_uploader(
                request,
                complaint=complaint
            )
        )


        if not uploaded_by:

            evidence_failed = (
                len(
                    evidence_files
                )
            )


            print(
                "EVIDENCE SAVE ERROR: "
                "No valid uploaded_by user "
                "could be determined."
            )


        else:

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


    # =====================================================
    # SUCCESS / WARNING MESSAGE
    # =====================================================

    if (
        evidence_saved > 0
        and
        evidence_failed == 0
    ):

        messages.success(
            request,
            (
                f"Complaint #CP-"
                f"{complaint.complaint_id:04d} "
                "was updated successfully "
                f"with {evidence_saved} "
                "new evidence file"
                f"{'s' if evidence_saved != 1 else ''}."
            )
        )


    elif (
        evidence_saved > 0
        and
        evidence_failed > 0
    ):

        messages.warning(
            request,
            (
                f"Complaint #CP-"
                f"{complaint.complaint_id:04d} "
                "was updated. "
                f"{evidence_saved} evidence "
                "file"
                f"{'s were' if evidence_saved != 1 else ' was'} "
                "saved, but "
                f"{evidence_failed} "
                "could not be uploaded."
            )
        )


    elif evidence_failed > 0:

        messages.warning(
            request,
            (
                f"Complaint #CP-"
                f"{complaint.complaint_id:04d} "
                "was updated, but the "
                "selected evidence files "
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


    # =====================================================
    # REDIRECT
    # =====================================================

    return redirect(
        "complaints"
    )


# =========================================================
# NEW COMPLAINT
# =========================================================

def new_complaint(request):

    # =====================================================
    # RESIDENTS
    # =====================================================

    residents = (
        Resident.objects
        .all()
        .order_by("resident_id")
    )


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        # =================================================
        # RESIDENT
        # =================================================

        resident_id = request.POST.get(
            "resident_id"
        )


        # =================================================
        # REPORT TYPE
        # =================================================

        report_type = request.POST.get(
            "report_type",
            "Formal Complaint"
        ).strip()


        # =================================================
        # COMPLAINT DETAILS
        # =================================================

        complaint_type = request.POST.get(
            "complaint_type",
            ""
        ).strip()


        subject = request.POST.get(
            "subject",
            ""
        ).strip()


        description = request.POST.get(
            "description",
            ""
        ).strip()


        # =================================================
        # INCIDENT INFORMATION
        # =================================================

        location = request.POST.get(
            "location",
            ""
        ).strip()


        incident_date = request.POST.get(
            "incident_date",
            ""
        ).strip()


        incident_time = request.POST.get(
            "incident_time",
            ""
        ).strip()


        # =================================================
        # RESPONDENT INFORMATION
        # =================================================

        respondent_name = request.POST.get(
            "respondent_name",
            ""
        ).strip()


        respondent_address = request.POST.get(
            "respondent_address",
            ""
        ).strip()


        respondent_relationship = (
            request.POST.get(
                "respondent_relationship",
                ""
            ).strip()
        )


        respondent_contact = request.POST.get(
            "respondent_contact",
            ""
        ).strip()


        # =================================================
        # EVIDENCE FILES
        # =================================================

        evidence_files = (
            request.FILES.getlist(
                "evidence"
            )
        )


        # =================================================
        # VALIDATE RESIDENT
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


        # =================================================
        # VALIDATE REQUIRED FIELDS
        # =================================================

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


        # =================================================
        # VALIDATE REPORT TYPE
        # =================================================

        if (
            report_type
            not in ALLOWED_REPORT_TYPES
        ):

            report_type = (
                "Formal Complaint"
            )


        # =================================================
        # COMMUNITY ISSUE
        # =================================================

        if (
            report_type
            ==
            "Community Issue"
        ):

            respondent_name = None
            respondent_address = None
            respondent_relationship = None
            respondent_contact = None


        # =================================================
        # VALIDATE EVIDENCE
        # =================================================

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
        # CREATE COMPLAINT
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
                (
                    "The complaint could not "
                    "be created. Please try again."
                )
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
        # DETERMINE EVIDENCE UPLOADER
        # =================================================

        uploaded_by = (
            get_evidence_uploader(
                request,
                complaint=complaint,
                resident=resident
            )
        )


        # =================================================
        # SAVE EVIDENCE
        # =================================================

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


        # =================================================
        # SUCCESS MESSAGE
        # =================================================

        if (
            evidence_saved > 0
            and
            evidence_failed == 0
        ):

            messages.success(
                request,
                (
                    f"Complaint #CP-"
                    f"{complaint.complaint_id:04d} "
                    "was created successfully "
                    f"with {evidence_saved} "
                    "evidence file"
                    f"{'s' if evidence_saved != 1 else ''}."
                )
            )


        elif (
            evidence_saved > 0
            and
            evidence_failed > 0
        ):

            messages.warning(
                request,
                (
                    f"Complaint #CP-"
                    f"{complaint.complaint_id:04d} "
                    "was created. "
                    f"{evidence_saved} evidence "
                    "file"
                    f"{'s were' if evidence_saved != 1 else ' was'} "
                    "saved, but "
                    f"{evidence_failed} "
                    "could not be uploaded."
                )
            )


        elif evidence_failed > 0:

            messages.warning(
                request,
                (
                    f"Complaint #CP-"
                    f"{complaint.complaint_id:04d} "
                    "was created, but the "
                    "evidence files could not "
                    "be uploaded."
                )
            )


        else:

            messages.success(
                request,
                (
                    f"Complaint #CP-"
                    f"{complaint.complaint_id:04d} "
                    "was created successfully."
                )
            )


        # =================================================
        # REDIRECT
        # =================================================

        return redirect(
            "complaints"
        )


    # =====================================================
    # GET
    # =====================================================

    context = {

        "residents":
            residents,
    }


    return render(
        request,
        "complaintmodule/newcomplaint.html",
        context
    )