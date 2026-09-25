from datetime import timedelta

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

    ".pdf",
    ".doc",
    ".docx",
    ".txt",
}


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

    complaints_list = all_complaints


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
            - timedelta(days=30)
        )

        complaints_list = (
            complaints_list.filter(
                submitted_at__gte=thirty_days_ago
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
            status="Under Investigation"
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
    #
    # Each table has its own GET parameter:
    #
    # new_page
    # ongoing_page
    # completed_page
    #
    # This means changing one table's page will not
    # change the page number of the other tables.
    #
    # =====================================================


    # -----------------------------------------------------
    # NEW COMPLAINTS PAGINATOR
    # -----------------------------------------------------

    new_paginator = Paginator(
        new_complaints_queryset,
        COMPLAINTS_PER_PAGE
    )


    new_page_number = request.GET.get(
        "new_page",
        1
    )


    new_page = new_paginator.get_page(
        new_page_number
    )


    # -----------------------------------------------------
    # ONGOING COMPLAINTS PAGINATOR
    # -----------------------------------------------------

    ongoing_paginator = Paginator(
        ongoing_complaints_queryset,
        COMPLAINTS_PER_PAGE
    )


    ongoing_page_number = request.GET.get(
        "ongoing_page",
        1
    )


    ongoing_page = ongoing_paginator.get_page(
        ongoing_page_number
    )


    # -----------------------------------------------------
    # COMPLETED COMPLAINTS PAGINATOR
    # -----------------------------------------------------

    completed_paginator = Paginator(
        completed_complaints_queryset,
        COMPLAINTS_PER_PAGE
    )


    completed_page_number = request.GET.get(
        "completed_page",
        1
    )


    completed_page = completed_paginator.get_page(
        completed_page_number
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
            status="Under Investigation"
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
                / total_complaints
            )
            * 100
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
            and complaint.updated_at
        ):

            difference = (
                complaint.updated_at
                - complaint.submitted_at
            )


            total_close_days += max(
                difference.days,
                0
            )


            close_count += 1


    if close_count > 0:

        average_close_days = round(
            total_close_days
            / close_count,
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
    # UPDATE COMPLAINT
    # =====================================================

    complaint.priority = priority

    complaint.status = status

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
    # SUCCESS MESSAGE
    # =====================================================

    messages.success(
        request,
        (
            f"Complaint #CP-"
            f"{complaint.complaint_id:04d} "
            f"was updated successfully."
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
            == "Community Issue"
        ):

            respondent_name = None

            respondent_address = None

            respondent_relationship = None

            respondent_contact = None


        # =================================================
        # VALIDATE NUMBER OF EVIDENCE FILES
        # =================================================

        if (
            len(evidence_files)
            > MAX_EVIDENCE_FILES
        ):

            messages.error(
                request,
                (
                    "You may upload a maximum "
                    f"of {MAX_EVIDENCE_FILES} "
                    "evidence files."
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
        # VALIDATE EACH EVIDENCE FILE
        # =================================================

        for uploaded_file in evidence_files:

            # ---------------------------------------------
            # FILE SIZE
            # ---------------------------------------------

            if (
                uploaded_file.size
                > MAX_EVIDENCE_FILE_SIZE
            ):

                messages.error(
                    request,
                    (
                        f"{uploaded_file.name} "
                        "exceeds the 10 MB "
                        "file size limit."
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


            # ---------------------------------------------
            # FILE EXTENSION
            # ---------------------------------------------

            file_name = (
                uploaded_file.name
                .lower()
            )


            file_extension = ""

            if "." in file_name:

                file_extension = (
                    "."
                    + file_name
                    .rsplit(".", 1)[1]
                )


            if (
                file_extension
                not in ALLOWED_EVIDENCE_EXTENSIONS
            ):

                messages.error(
                    request,
                    (
                        f"{uploaded_file.name} "
                        "is not a supported "
                        "evidence file type."
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

                    subject=subject,

                    description=description,

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
            request.session.get(
                "user_id"
            )
            or
            resident.resident_id
        )


        # =================================================
        # SAVE EVIDENCE
        # =================================================

        evidence_saved = 0

        evidence_failed = 0


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


        # =================================================
        # SUCCESS MESSAGE
        # =================================================

        if (
            evidence_saved > 0
            and evidence_failed == 0
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
            and evidence_failed > 0
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