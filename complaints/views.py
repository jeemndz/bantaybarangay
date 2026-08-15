from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Complaint
from residentmodule.models import Resident


def complaints(request):

    complaints_list = Complaint.objects.all().order_by("-submitted_at")

    total_complaints = complaints_list.count()

    pending_complaints = complaints_list.filter(
        status__in=[
            "New",
            "Under Investigation"
        ]
    ).count()

    resolved_complaints = complaints_list.filter(
        status="Resolved"
    ).count()

    if total_complaints > 0:
        resolved_percentage = round(
            (resolved_complaints / total_complaints) * 100
        )
    else:
        resolved_percentage = 0

    context = {
        "complaints": complaints_list,
        "total_complaints": total_complaints,
        "pending_complaints": pending_complaints,
        "resolved_percentage": resolved_percentage,
        "average_close_days": 0,
    }

    return render(
        request,
        "complaintmodule/complaints.html",
        context
    )


def new_complaint(request):

    # Get all existing residents
    residents = Resident.objects.all().order_by("resident_id")

    if request.method == "POST":

        resident_id = request.POST.get("resident_id")
        complaint_type = request.POST.get("complaint_type")
        subject = request.POST.get("subject")
        description = request.POST.get("description")
        location = request.POST.get("location")
        incident_date = request.POST.get("incident_date")
        priority = request.POST.get("priority")

        # Get the selected resident
        resident = get_object_or_404(
            Resident,
            resident_id=resident_id
        )

        # Create complaint
        Complaint.objects.create(
            resident=resident,
            complaint_type=complaint_type,
            subject=subject,
            description=description,
            location=location,
            incident_date=incident_date if incident_date else None,
            priority=priority,
            status="New",
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