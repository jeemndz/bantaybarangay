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
from django.utils import timezone
from django.views.decorators.http import require_POST
from urllib3 import request
from bantaybarangay.security import role_required
from .models import Evidence

from .services.fabric_service import (
    FabricServiceError,
    register_document,
    get_document,
    verify_document,
)

from .services.hashing import calculate_file_hash

from blockchain_logs.services.blockchain_logger import create_blockchain_log


# =========================================================
# EVIDENCE MANAGEMENT / LIST
# =========================================================
@role_required("admin", "official")
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
@role_required("admin", "official")
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
@role_required("admin", "official")
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

                "blockchain_status":
                    item.blockchain_status,

                "blockchain_tx_id":
                    item.blockchain_tx_id or "",

                "blockchain_registered_at":
                    (
                        item.blockchain_registered_at.strftime(
                            "%b %d, %Y %I:%M %p"
                        )
                        if item.blockchain_registered_at
                        else ""
                    ),

                "integrity_status":
                    item.integrity_status,

                "last_verified_at":
                    (
                        item.last_verified_at.strftime(
                            "%b %d, %Y %I:%M %p"
                        )
                        if item.last_verified_at
                        else ""
                    ),

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
@role_required("admin", "official")
def evidence_create(request):

    if request.method == "POST":

        complaint_id = request.POST.get(
            "complaint_id"
        )
        uploaded_by = request.session.get("user_id")

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
@role_required("admin", "official")
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


# =========================================================
# REGISTER EVIDENCE ON BLOCKCHAIN
# =========================================================
@role_required("admin", "official")
@require_POST
def register_evidence_blockchain(request, evidence_id):

    evidence = get_object_or_404(
        Evidence,
        evidence_id=evidence_id
    )

    document_id = f"EVD-{evidence.evidence_id}"

    recorded_by = str(
        request.session.get("username")
        or request.session.get("user_id")
        or "system"
    )

    try:

        # =================================================
        # CHECK IF DOCUMENT ALREADY EXISTS ON FABRIC
        # =================================================

        try:
            blockchain_document = get_document(
                document_id
            )

        except FabricServiceError:
            blockchain_document = None

        # =================================================
        # ALREADY REGISTERED ON FABRIC
        # =================================================

        if blockchain_document:

            blockchain_hash = blockchain_document.get(
                "fileHash",
                ""
            )

            # Existing Fabric ID has a different hash.
            if blockchain_hash != evidence.file_hash:

                evidence.blockchain_status = "Failed"

                evidence.save(
                    update_fields=[
                        "blockchain_status"
                    ]
                )

                create_blockchain_log(
                    blockchain_document_id=document_id,
                    document_id=evidence.evidence_id,
                    document_type="EVIDENCE",
                    document_hash=evidence.file_hash,
                    transaction_hash=None,
                    action="REGISTER",
                    status="FAILED",
                    verification_status="Failed",
                    error_message=(
                        "Evidence ID already exists on "
                        "Fabric with a different hash."
                    ),
                    recorded_by=recorded_by,
                )

                return JsonResponse(
                    {
                        "success": False,
                        "error": (
                            "This evidence ID already exists "
                            "on Fabric with a different hash."
                        ),
                    },
                    status=409,
                )

            # Existing document has the same hash.
            evidence.blockchain_status = "Registered"

            if not evidence.blockchain_registered_at:
                evidence.blockchain_registered_at = timezone.now()

            evidence.save(
                update_fields=[
                    "blockchain_status",
                    "blockchain_registered_at",
                ]
            )

            # This is an application audit entry.
            # There is no new Fabric transaction because the
            # document already existed.
            create_blockchain_log(
                blockchain_document_id=document_id,
                document_id=evidence.evidence_id,
                document_type="EVIDENCE",
                document_hash=evidence.file_hash,
                transaction_hash=evidence.blockchain_tx_id,
                action="REGISTER",
                status="SUCCESS",
                verification_status="Pending",
                recorded_by=recorded_by,
            )

            return JsonResponse(
                {
                    "success": True,
                    "already_registered": True,
                    "document_id": document_id,
                    "message": (
                        "Evidence already exists on Fabric "
                        "and the stored hash matches."
                    ),
                }
            )

        # =================================================
        # NEW FABRIC REGISTRATION
        # =================================================

        registered_by = recorded_by

        result = register_document(
            document_id=document_id,
            complaint_id=evidence.complaint_id,
            document_type="EVIDENCE",
            file_name=evidence.file_name,
            file_hash=evidence.file_hash,
            registered_by=registered_by,
        )

        evidence.blockchain_status = "Registered"

        evidence.blockchain_tx_id = result.get(
            "transactionId"
        )

        evidence.blockchain_registered_at = timezone.now()

        evidence.save(
            update_fields=[
                "blockchain_status",
                "blockchain_tx_id",
                "blockchain_registered_at",
            ]
        )

        # =================================================
        # BLOCKCHAIN AUDIT LOG - SUCCESSFUL REGISTRATION
        # =================================================

        create_blockchain_log(
            blockchain_document_id=document_id,
            document_id=evidence.evidence_id,
            document_type="EVIDENCE",
            document_hash=evidence.file_hash,
            transaction_hash=evidence.blockchain_tx_id,
            action="REGISTER",
            status="SUCCESS",
            verification_status="Pending",
            recorded_by=recorded_by,
        )

        return JsonResponse(
            {
                "success": True,
                "already_registered": False,
                "document_id": document_id,
                "transaction_id":
                    evidence.blockchain_tx_id,
                "message": (
                    "Evidence successfully registered "
                    "on Hyperledger Fabric."
                ),
            }
        )

    except FabricServiceError as error:

        evidence.blockchain_status = "Failed"

        evidence.save(
            update_fields=[
                "blockchain_status"
            ]
        )

        # =================================================
        # BLOCKCHAIN AUDIT LOG - FAILED REGISTRATION
        # =================================================

        create_blockchain_log(
            blockchain_document_id=document_id,
            document_id=evidence.evidence_id,
            document_type="EVIDENCE",
            document_hash=evidence.file_hash,
            transaction_hash=None,
            action="REGISTER",
            status="FAILED",
            verification_status="Failed",
            error_message=str(error),
            recorded_by=recorded_by,
        )

        return JsonResponse(
            {
                "success": False,
                "error": str(error),
            },
            status=502,
        )


# =========================================================
# VERIFY EVIDENCE INTEGRITY
# =========================================================
@role_required("admin", "official")
@require_POST
def verify_evidence_integrity(request, evidence_id):

    evidence = get_object_or_404(
        Evidence,
        evidence_id=evidence_id
    )

    document_id = f"EVD-{evidence.evidence_id}"

    recorded_by = str(
        request.session.get("username")
        or request.session.get("user_id")
        or "system"
    )

    if evidence.blockchain_status != "Registered":

        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Evidence must be registered on "
                    "Fabric before verification."
                ),
            },
            status=400,
        )

    if not evidence.file_path:

        return JsonResponse(
            {
                "success": False,
                "error": "Evidence file path is missing.",
            },
            status=400,
        )

    # Convert:
    #
    # /media/evidence/complaint_19/file.jpg
    #
    # into:
    #
    # evidence/complaint_19/file.jpg

    relative_path = (
        str(evidence.file_path)
        .replace("/media/", "", 1)
        .lstrip("/\\")
    )

    physical_path = os.path.join(
        settings.MEDIA_ROOT,
        relative_path
    )

    if not os.path.isfile(
        physical_path
    ):

        return JsonResponse(
            {
                "success": False,
                "error":
                    "Evidence file could not be found.",
            },
            status=404,
        )

    try:

        # =================================================
        # HASH ACTUAL CURRENT FILE
        # =================================================

        current_hash = calculate_file_hash(
            physical_path
        )

        # =================================================
        # VERIFY AGAINST FABRIC
        # =================================================

        verified = verify_document(
            document_id,
            current_hash,
        )

        evidence.last_verified_at = timezone.now()

        if verified:
            evidence.integrity_status = "Verified"
        else:
            evidence.integrity_status = "Failed"

        evidence.save(
            update_fields=[
                "integrity_status",
                "last_verified_at",
            ]
        )

        # =================================================
        # BLOCKCHAIN AUDIT LOG - VERIFICATION RESULT
        # =================================================

        create_blockchain_log(
            blockchain_document_id=document_id,
            document_id=evidence.evidence_id,
            document_type="EVIDENCE",
            document_hash=current_hash,
            transaction_hash=None,
            action="VERIFY",
            status="SUCCESS",
            verification_status=(
                "Confirmed"
                if verified
                else "Failed"
            ),
            recorded_by=recorded_by,
        )

        return JsonResponse(
            {
                "success": True,
                "document_id": document_id,
                "verified": verified,
                "integrity_status":
                    evidence.integrity_status,
                "current_hash": current_hash,
                "last_verified_at":
                    evidence.last_verified_at.isoformat(),
            }
        )

    except FabricServiceError as error:

        # =================================================
        # BLOCKCHAIN AUDIT LOG - VERIFICATION ERROR
        # =================================================

        create_blockchain_log(
            blockchain_document_id=document_id,
            document_id=evidence.evidence_id,
            document_type="EVIDENCE",
            document_hash=(
                current_hash
                if "current_hash" in locals()
                else evidence.file_hash
            ),
            transaction_hash=None,
            action="VERIFY",
            status="FAILED",
            verification_status="Failed",
            error_message=str(error),
            recorded_by=recorded_by,
        )

        return JsonResponse(
            {
                "success": False,
                "error": str(error),
            },
            status=502,
        )