from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from complaints.models import Complaint
from residentmodule.models import Resident
from .models import Evidence

import hashlib
import os


# =========================================================
# EVIDENCE LIST
# =========================================================

def evidence_list(request):

    evidence = Evidence.objects.all().order_by("-uploaded_at")

    complaints = Complaint.objects.all().order_by("-submitted_at")

    residents = Resident.objects.all().order_by(
        "last_name",
        "first_name"
    )

    complaint_data = []

    for complaint in complaints:

        resident = Resident.objects.filter(
            resident_id=complaint.resident_id
        ).first()

        if resident:

            name_parts = [
                resident.first_name,
                resident.middle_name,
                resident.last_name,
                resident.suffix
            ]

            resident_name = " ".join(
                part for part in name_parts if part
            )

        else:
            resident_name = "Unknown Resident"

        complaint_data.append({
            "complaint_id": complaint.complaint_id,
            "resident_name": resident_name,
            "subject": complaint.subject,
            "status": complaint.status,
        })

    return render(
        request,
        "evidencemodule/evidence_list.html",
        {
            "evidence": evidence,
            "complaints": complaint_data,
            "residents": residents,
        }
    )


# =========================================================
# GET COMPLAINTS FOR SELECTED RESIDENT
# =========================================================

def resident_complaints(request, resident_id):

    complaints = Complaint.objects.filter(
        resident_id=resident_id
    ).order_by("-submitted_at")

    complaint_data = []

    for complaint in complaints:

        complaint_data.append({
            "complaint_id": complaint.complaint_id,
            "subject": complaint.subject,
            "status": complaint.status,
        })

    return JsonResponse({
        "complaints": complaint_data
    })


# =========================================================
# EVIDENCE DETAIL
# =========================================================

def evidence_detail(request, evidence_id):

    evidence = get_object_or_404(
        Evidence,
        evidence_id=evidence_id
    )

    return render(
        request,
        "evidencemodule/evidence_detail.html",
        {
            "evidence": evidence
        }
    )


# =========================================================
# CREATE EVIDENCE
# =========================================================

def evidence_create(request):

    if request.method == "POST":

        complaint_id = request.POST.get("complaint_id")
        uploaded_file = request.FILES.get("file")

        if not complaint_id or not uploaded_file:
            return redirect(
                "evidencemodule:evidence_list"
            )

        # ---------------------------------------------
        # Verify complaint
        # ---------------------------------------------

        complaint = get_object_or_404(
            Complaint,
            complaint_id=complaint_id
        )

        # ---------------------------------------------
        # Calculate SHA-256
        # ---------------------------------------------

        file_data = uploaded_file.read()

        file_hash = hashlib.sha256(
            file_data
        ).hexdigest()

        # ---------------------------------------------
        # Evidence directory
        # ---------------------------------------------

        evidence_directory = os.path.join(
            settings.MEDIA_ROOT,
            "evidence"
        )

        os.makedirs(
            evidence_directory,
            exist_ok=True
        )

        # ---------------------------------------------
        # Filename
        # ---------------------------------------------

        original_name = uploaded_file.name

        file_path = os.path.join(
            evidence_directory,
            original_name
        )

        # ---------------------------------------------
        # Prevent duplicate filenames
        # ---------------------------------------------

        if os.path.exists(file_path):

            name, extension = os.path.splitext(
                original_name
            )

            original_name = (
                f"{name}_{file_hash[:8]}{extension}"
            )

            file_path = os.path.join(
                evidence_directory,
                original_name
            )

        # ---------------------------------------------
        # Save file
        # ---------------------------------------------

        with open(file_path, "wb") as destination:
            destination.write(file_data)

        database_file_path = (
            f"evidence/{original_name}"
        )

        # ---------------------------------------------
        # Logged-in officer
        # ---------------------------------------------

        uploaded_by = request.session.get("user_id")

        if not uploaded_by:
            return redirect("login")

        # ---------------------------------------------
        # Save database record
        # ---------------------------------------------

        Evidence.objects.create(
    complaint_id=complaint.complaint_id,
    uploaded_by=uploaded_by,
    file_name=original_name,
    file_path=database_file_path,
    file_type=uploaded_file.content_type,
    file_size=uploaded_file.size,
    file_hash=file_hash,
    uploaded_at=timezone.now()
)

        return redirect(
            "evidencemodule:evidence_list"
        )

    return redirect(
        "evidencemodule:evidence_list"
    )


# =========================================================
# DELETE EVIDENCE
# =========================================================

def evidence_delete(request, evidence_id):

    evidence = get_object_or_404(
        Evidence,
        evidence_id=evidence_id
    )

    if request.method == "POST":

        evidence.delete()

        return redirect(
            "evidencemodule:evidence_list"
        )

    return render(
        request,
        "evidencemodule/evidence_delete.html",
        {
            "evidence": evidence
        }
    )