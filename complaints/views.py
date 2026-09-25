from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import Complaint
from residentmodule.models import Resident


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
# COMPLAINT MANAGEMENT
# =========================================================

def complaints(request):

    # =====================================================
    # ALL COMPLAINTS
    # =====================================================

    all_complaints = Complaint.objects.all().order_by(
        "-submitted_at"
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

        complaints_list = complaints_list.filter(
            complaint_type=category
        )


    # -----------------------------------------------------
    # STATUS FILTER
    # -----------------------------------------------------

    if status:

        complaints_list = complaints_list.filter(
            status=status
        )


    # -----------------------------------------------------
    # LAST 30 DAYS
    # -----------------------------------------------------

    if date_range == "30":

        thirty_days_ago = (
            timezone.now()
            - timezone.timedelta(days=30)
        )

        complaints_list = complaints_list.filter(
            submitted_at__gte=thirty_days_ago
        )


    # =====================================================
    # SPLIT INTO THREE TABLES
    # =====================================================

    new_complaints = complaints_list.filter(
        status__in=[
            "Submitted",
            "Under Review",
        ]
    )


    ongoing_complaints = complaints_list.filter(
        status="Under Investigation"
    )


    completed_complaints = complaints_list.filter(
        status__in=[
            "Resolved",
            "Rejected",
            "Closed",
        ]
    )


    # =====================================================
    # STATISTICS
    # =====================================================

    total_complaints = all_complaints.count()


    pending_complaints = all_complaints.filter(
        status__in=[
            "Submitted",
            "Under Review",
            "Under Investigation",
        ]
    ).count()


    ongoing_count = all_complaints.filter(
        status="Under Investigation"
    ).count()


    resolved_complaints = all_complaints.filter(
        status="Resolved"
    ).count()


    completed_count = all_complaints.filter(
        status__in=[
            "Resolved",
            "Rejected",
            "Closed",
        ]
    ).count()


    # =====================================================
    # RESOLVED PERCENTAGE
    # =====================================================

    if total_complaints > 0:

        resolved_percentage = round(
            (
                resolved_complaints
                / total_complaints
            ) * 100
        )

    else:

        resolved_percentage = 0


    # =====================================================
    # AVERAGE TIME TO CLOSE
    # =====================================================

    completed_for_average = all_complaints.filter(
        status__in=[
            "Resolved",
            "Closed",
        ]
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
            total_close_days / close_count,
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
            new_complaints,

        "ongoing_complaints":
            ongoing_complaints,

        "completed_complaints":
            completed_complaints,

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
    }


    return render(
        request,
        "complaintmodule/complaints.html",
        context
    )


# =========================================================
# UPDATE COMPLAINT REVIEW
# =========================================================

@require_POST
def update_complaint(request, complaint_id):

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

    if priority not in ALLOWED_COMPLAINT_PRIORITIES:

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

    if status not in ALLOWED_COMPLAINT_STATUSES:

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

    complaint.updated_at = timezone.now()


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

    residents = Resident.objects.all().order_by(
        "resident_id"
    )


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        # -------------------------------------------------
        # RESIDENT
        # -------------------------------------------------

        resident_id = request.POST.get(
            "resident_id"
        )


        # -------------------------------------------------
        # REPORT TYPE
        # -------------------------------------------------

        report_type = request.POST.get(
            "report_type",
            "Formal Complaint"
        ).strip()


        # -------------------------------------------------
        # COMPLAINT DETAILS
        # -------------------------------------------------

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


        # -------------------------------------------------
        # INCIDENT INFORMATION
        # -------------------------------------------------

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


        # -------------------------------------------------
        # RESPONDENT
        # -------------------------------------------------

        respondent_name = request.POST.get(
            "respondent_name",
            ""
        ).strip()

        respondent_address = request.POST.get(
            "respondent_address",
            ""
        ).strip()

        respondent_relationship = request.POST.get(
            "respondent_relationship",
            ""
        ).strip()

        respondent_contact = request.POST.get(
            "respondent_contact",
            ""
        ).strip()


        # =================================================
        # CHECK RESIDENT
        # =================================================

        get_object_or_404(
            Resident,
            resident_id=resident_id
        )


        # =================================================
        # VALIDATE REPORT TYPE
        # =================================================

        if report_type not in ALLOWED_REPORT_TYPES:

            report_type = "Formal Complaint"


        # =================================================
        # COMMUNITY ISSUE
        # =================================================

        if report_type == "Community Issue":

            respondent_name = None
            respondent_address = None
            respondent_relationship = None
            respondent_contact = None


        # =================================================
        # CREATE COMPLAINT
        # =================================================

        Complaint.objects.create(

            resident_id=resident_id,

            report_type=report_type,

            complaint_type=complaint_type,

            subject=subject,

            description=description,

            location=(
                location or None
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
                respondent_name or None
            ),

            respondent_address=(
                respondent_address or None
            ),

            respondent_relationship=(
                respondent_relationship or None
            ),

            respondent_contact=(
                respondent_contact or None
            ),

            priority="N/A",

            status="Submitted",

            assigned_official=None,

            resolution=None,

            submitted_at=timezone.now(),

            updated_at=timezone.now(),
        )


        messages.success(
            request,
            "Complaint created successfully."
        )


        return redirect(
            "complaints"
        )


    # =====================================================
    # GET
    # =====================================================

    context = {
        "residents": residents,
    }


    return render(
        request,
        "complaintmodule/newcomplaint.html",
        context
    )