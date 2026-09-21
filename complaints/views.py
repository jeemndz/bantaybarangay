from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Complaint
from residentmodule.models import Resident


def complaints(request):

    # ALL COMPLAINTS
    all_complaints = Complaint.objects.all().order_by("-submitted_at")

    # FILTER VALUES
    category = request.GET.get("category", "")
    status = request.GET.get("status", "")
    date_range = request.GET.get("date_range", "")

    # FILTERED COMPLAINTS
    complaints_list = all_complaints

    # CATEGORY
    if category:
        complaints_list = complaints_list.filter(
            complaint_type=category
        )

    # STATUS
    if status:
        complaints_list = complaints_list.filter(
            status=status
        )

    # LAST 30 DAYS
    if date_range == "30":
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)

        complaints_list = complaints_list.filter(
            submitted_at__gte=thirty_days_ago
        )

    # =========================
    # STATISTICS
    # =========================

    total_complaints = all_complaints.count()

    pending_complaints = all_complaints.filter(
        status__in=[
            "Submitted",
            "Under Review",
            "Under Investigation"
        ]
    ).count()

    resolved_complaints = all_complaints.filter(
        status="Resolved"
    ).count()

    if total_complaints > 0:
        resolved_percentage = round(
            (resolved_complaints / total_complaints) * 100
        )
    else:
        resolved_percentage = 0

    context = {
        # Filtered table
        "complaints": complaints_list,

        # Overall statistics
        "total_complaints": total_complaints,
        "pending_complaints": pending_complaints,
        "resolved_percentage": resolved_percentage,
        "average_close_days": 0,

        # Selected filters
        "selected_category": category,
        "selected_status": status,
        "selected_date_range": date_range,
    }

    return render(
        request,
        "complaintmodule/complaints.html",
        context
    )


def new_complaint(request):

    residents = Resident.objects.all().order_by("resident_id")

    if request.method == "POST":

        resident_id = request.POST.get("resident_id")
        complaint_type = request.POST.get("complaint_type")
        subject = request.POST.get("subject")
        description = request.POST.get("description")
        location = request.POST.get("location")
        incident_date = request.POST.get("incident_date")
        priority = request.POST.get("priority")

        # Check that resident exists
        get_object_or_404(
            Resident,
            resident_id=resident_id
        )

        # Create complaint
        Complaint.objects.create(
            resident_id=resident_id,
            complaint_type=complaint_type,
            subject=subject,
            description=description,
            location=location,
            incident_date=incident_date if incident_date else None,
            priority=priority,
            status="Submitted",
            submitted_at=timezone.now(),
            updated_at=timezone.now(),
        )

        return redirect("complaints")

    context = {
        "residents": residents,
    }

    return render(
        request,
        "complaintmodule/newcomplaint.html",
        context
    )