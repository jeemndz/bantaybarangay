import hashlib
import os

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.views.decorators.http import require_GET

from .models import Evidence


# =========================================================
# EVIDENCE MANAGEMENT / LIST
# =========================================================

def evidence_list(request):

    evidence = (
        Evidence.objects
        .all()
        .order_by("-uploaded_at")
    )

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
# EVIDENCE BY COMPLAINT
# Used by Complaint Review modal
# =========================================================

@require_GET
def complaint_evidence(request, complaint_id):

    evidence_items = (
        Evidence.objects
        .filter(
            complaint_id=complaint_id
        )
        .order_by("-uploaded_at")
    )

    results = []

    for item in evidence_items:

        file_url = ""

        if item.file_path:

            file_path = str(
                item.file_path
            ).replace("\\", "/")

            # Already a complete URL
            if (
                file_path.startswith("http://")
                or
                file_path.startswith("https://")
            ):

                file_url = file_path

            # Already starts with /media/
            elif file_path.startswith("/media/"):

                file_url = file_path

            # Stored as media-relative path
            else:

                media_url = getattr(
                    settings,
                    "MEDIA_URL",
                    "/media/"
                )

                file_url = (
                    media_url.rstrip("/")
                    + "/"
                    + file_path.lstrip("/")
                )

        results.append(
            {
                "evidence_id":
                    item.evidence_id,

                "complaint_id":
                    item.complaint_id,

                "file_name":
                    item.file_name,

                "file_path":
                    file_url,

                "file_type":
                    item.file_type,

                "file_size":
                    item.file_size,

                "file_hash":
                    item.file_hash,

                "uploaded_at":
                    (
                        item.uploaded_at.strftime(
                            "%b %d, %Y %I:%M %p"
                        )
                        if item.uploaded_at
                        else ""
                    ),
            }
        )

    return JsonResponse(
        {
            "complaint_id": complaint_id,
            "count": len(results),
            "evidence": results,
        }
    )


# =========================================================
# CREATE EVIDENCE
# =========================================================

def evidence_create(request):

    if request.method == "POST":

        complaint_id = request.POST.get(
            "complaint_id"
        )

        uploaded_by = (
            request.session.get("user_id")
            or
            request.POST.get("uploaded_by")
        )

        uploaded_file = request.FILES.get(
            "file"
        )

        # =================================================
        # ACTUAL FILE UPLOAD
        # =================================================

        if uploaded_file:

            evidence = save_evidence_file(
                uploaded_file=uploaded_file,
                complaint_id=complaint_id,
                uploaded_by=uploaded_by,
            )

            if request.headers.get(
                "x-requested-with"
            ) == "XMLHttpRequest":

                return JsonResponse(
                    {
                        "success": True,
                        "evidence_id":
                            evidence.evidence_id,
                    }
                )

            return redirect(
                "evidencemodule:evidence_list"
            )

        # =================================================
        # LEGACY MANUAL RECORD CREATION
        # =================================================

        file_name = request.POST.get(
            "file_name",
            ""
        )

        file_path = request.POST.get(
            "file_path",
            ""
        )

        file_type = request.POST.get(
            "file_type",
            ""
        )

        file_size = request.POST.get(
            "file_size",
            0
        )

        file_hash = request.POST.get(
            "file_hash",
            ""
        )

        Evidence.objects.create(
            complaint_id=complaint_id,
            uploaded_by=uploaded_by,
            file_name=file_name,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            file_hash=file_hash,
        )

        return redirect(
            "evidencemodule:evidence_list"
        )

    return render(
        request,
        "evidencemodule/evidence_create.html"
    )


# =========================================================
# SAVE EVIDENCE FILE
# Reusable by complaint submission
# =========================================================

def save_evidence_file(
    uploaded_file,
    complaint_id,
    uploaded_by,
):

    # =====================================================
    # DIRECTORY
    # =====================================================

    relative_directory = os.path.join(
        "evidence",
        f"complaint_{complaint_id}",
    )

    absolute_directory = os.path.join(
        settings.MEDIA_ROOT,
        relative_directory,
    )

    os.makedirs(
        absolute_directory,
        exist_ok=True
    )


    # =====================================================
    # SAFE FILE NAME
    # =====================================================

    original_name = os.path.basename(
        uploaded_file.name
    )

    base_name, extension = os.path.splitext(
        original_name
    )

    safe_base_name = "".join(
        character
        if (
            character.isalnum()
            or character in "-_"
        )
        else "_"
        for character in base_name
    )

    if not safe_base_name:
        safe_base_name = "evidence"

    safe_name = (
        safe_base_name
        + extension.lower()
    )


    # =====================================================
    # PREVENT OVERWRITE
    # =====================================================

    final_name = safe_name

    counter = 1

    while os.path.exists(
        os.path.join(
            absolute_directory,
            final_name
        )
    ):

        final_name = (
            f"{safe_base_name}_{counter}"
            f"{extension.lower()}"
        )

        counter += 1


    absolute_path = os.path.join(
        absolute_directory,
        final_name
    )


    # =====================================================
    # SAVE + SHA-256 HASH
    # =====================================================

    sha256 = hashlib.sha256()

    with open(
        absolute_path,
        "wb+"
    ) as destination:

        for chunk in uploaded_file.chunks():

            destination.write(
                chunk
            )

            sha256.update(
                chunk
            )


    # =====================================================
    # DATABASE PATH
    # =====================================================

    relative_path = os.path.join(
        relative_directory,
        final_name,
    ).replace("\\", "/")


    # =====================================================
    # CREATE EVIDENCE RECORD
    # =====================================================

    evidence = Evidence.objects.create(

        complaint_id=complaint_id,

        uploaded_by=uploaded_by,

        file_name=original_name,

        file_path=relative_path,

        file_type=(
            uploaded_file.content_type
            or
            "application/octet-stream"
        ),

        file_size=uploaded_file.size,

        file_hash=sha256.hexdigest(),
    )

    return evidence


# =========================================================
# DELETE EVIDENCE
# =========================================================

def evidence_delete(request, evidence_id):

    evidence = get_object_or_404(
        Evidence,
        evidence_id=evidence_id
    )

    if request.method == "POST":

        # Delete physical file when possible
        if evidence.file_path:

            try:

                physical_path = os.path.join(
                    settings.MEDIA_ROOT,
                    evidence.file_path
                )

                if os.path.isfile(
                    physical_path
                ):
                    os.remove(
                        physical_path
                    )

            except Exception as error:

                print(
                    "EVIDENCE FILE DELETE ERROR:",
                    error
                )

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