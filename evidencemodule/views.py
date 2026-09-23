from django.shortcuts import render, redirect, get_object_or_404
from .models import Evidence


# =========================================================
# EVIDENCE MANAGEMENT / LIST
# =========================================================

def evidence_list(request):

    evidence = Evidence.objects.all().order_by("-uploaded_at")

    context = {
        "evidence": evidence
    }

    return render(
        request,
        "evidencemodule/evidence_list.html",
        context
    )


# =========================================================
# EVIDENCE DETAIL
# =========================================================

def evidence_detail(request, evidence_id):

    evidence = get_object_or_404(
        Evidence,
        evidence_id=evidence_id
    )

    context = {
        "evidence": evidence
    }

    return render(
        request,
        "evidencemodule/evidence_detail.html",
        context
    )


# =========================================================
# CREATE EVIDENCE
# =========================================================

def evidence_create(request):

    if request.method == "POST":

        complaint_id = request.POST.get("complaint_id")
        uploaded_by = request.POST.get("uploaded_by")
        file_name = request.POST.get("file_name")
        file_path = request.POST.get("file_path")
        file_type = request.POST.get("file_type")
        file_size = request.POST.get("file_size")
        file_hash = request.POST.get("file_hash")

        Evidence.objects.create(
            complaint_id=complaint_id,
            uploaded_by=uploaded_by,
            file_name=file_name,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            file_hash=file_hash
        )

        return redirect(
            "evidencemodule:evidence_list"
        )

    return render(
        request,
        "evidencemodule/evidence_create.html"
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