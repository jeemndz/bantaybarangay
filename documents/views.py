import os

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Document, DocumentType, ComplaintDocument
from registration.models import Resident
from bantaybarangay.security import role_required
from evidencemodule.services.fabric_service import (
    FabricServiceError,
    register_document,
    get_document,
    verify_document,
)

from evidencemodule.services.hashing import calculate_file_hash
from blockchain_logs.services.blockchain_logger import create_blockchain_log
from documents.services.complaint_pdf import generate_complaint_pdf


# =========================================================
# DOCUMENT LIST
# =========================================================
@role_required("admin", "official")
def document_list(request):

    documents = (
        Document.objects
        .select_related("document_type")
        .all()
        .order_by("-document_id")
    )

    # Search
    search = request.GET.get("search", "").strip()

    if search:
        documents = documents.filter(
            document_number__icontains=search
        )

    # Filter by type
    selected_type = request.GET.get(
        "document_type",
        ""
    ).strip()

    if selected_type:
        documents = documents.filter(
            document_type__type_name=selected_type
        )

    # Filter by status
    selected_status = request.GET.get(
        "status",
        ""
    ).strip()

    if selected_status:
        documents = documents.filter(
            status=selected_status
        )

    # Statistics
    total_documents = Document.objects.count()

    verified_documents = Document.objects.filter(
        status="Verified"
    ).count()

    pending_documents = Document.objects.filter(
        status="Pending"
    ).count()

    # Document templates
    document_types = DocumentType.objects.filter(
        status="Active"
    ).order_by("type_name")

    # Residents
    residents = Resident.objects.all()

    resident_dict = {
        resident.resident_id: resident
        for resident in residents
    }

    # Attach resident
    for document in documents:
        document.resident = resident_dict.get(
            document.resident_id
        )

    context = {
        "documents": documents,
        "document_types": document_types,
        "total_documents": total_documents,
        "verified_documents": verified_documents,
        "pending_documents": pending_documents,
        "search": search,
        "selected_type": selected_type,
        "selected_status": selected_status,
    }

    return render(
        request,
        "documentmodule/document_list.html",
        context
    )


# =========================================================
# GENERATE OFFICIAL COMPLAINT PDF
# =========================================================

@require_POST
def generate_official_complaint_document(
    request,
    complaint_id
):
    """
    Generates the official complaint PDF.

    If a ComplaintDocument already exists for this complaint,
    the existing document is returned instead of generating
    another copy.
    """

    try:

        # -------------------------------------------------
        # CHECK IF DOCUMENT ALREADY EXISTS
        # -------------------------------------------------

        existing_document = (
            ComplaintDocument.objects
            .filter(complaint_id=complaint_id)
            .first()
        )

        if existing_document:

            return JsonResponse(
                {
                    "success": True,
                    "already_exists": True,
                    "document_id":
                        existing_document.document_id,
                    "complaint_id":
                        existing_document.complaint_id,
                    "file_name":
                        existing_document.file_name,
                    "blockchain_status":
                        existing_document.blockchain_status,
                    "integrity_status":
                        existing_document.integrity_status,
                    "message": (
                        "An official complaint document "
                        "already exists for this complaint."
                    ),
                }
            )

        # -------------------------------------------------
        # GENERATE PDF
        # -------------------------------------------------

        document = generate_complaint_pdf(
            complaint_id
        )

        return JsonResponse(
            {
                "success": True,
                "already_exists": False,
                "document_id":
                    document.document_id,
                "complaint_id":
                    document.complaint_id,
                "file_name":
                    document.file_name,
                "blockchain_status":
                    document.blockchain_status,
                "integrity_status":
                    document.integrity_status,
                "message": (
                    "Official complaint PDF "
                    "generated successfully."
                ),
            }
        )

    except Exception as error:

        return JsonResponse(
            {
                "success": False,
                "error": str(error),
            },
            status=500,
        )


# =========================================================
# GET OFFICIAL COMPLAINT DOCUMENT
# =========================================================
@role_required("admin", "official")
def complaint_document(request, complaint_id):

    try:

        document = ComplaintDocument.objects.get(
            complaint_id=complaint_id
        )

    except ComplaintDocument.DoesNotExist:

        return JsonResponse(
            {
                "success": True,
                "exists": False,
                "document": None,
            }
        )

    # Build file URL
    file_url = ""

    if document.file_path:

        relative_path = (
            str(document.file_path)
            .replace("\\", "/")
            .replace("/media/", "", 1)
            .lstrip("/")
        )

        file_url = (
            settings.MEDIA_URL.rstrip("/")
            + "/"
            + relative_path
        )

    return JsonResponse(
        {
            "success": True,
            "exists": True,

            "document": {
                "document_id":
                    document.document_id,

                "complaint_id":
                    document.complaint_id,

                "document_type":
                    document.document_type,

                "file_name":
                    document.file_name,

                "file_path":
                    document.file_path,

                "file_url":
                    file_url,

                "file_hash":
                    document.file_hash,

                "blockchain_status":
                    document.blockchain_status,

                "blockchain_tx_id":
                    document.blockchain_tx_id or "",

                "blockchain_registered_at": (
                    document.blockchain_registered_at.isoformat()
                    if document.blockchain_registered_at
                    else ""
                ),

                "integrity_status":
                    document.integrity_status,

                "last_verified_at": (
                    document.last_verified_at.isoformat()
                    if document.last_verified_at
                    else ""
                ),

                "generated_at": (
                    document.generated_at.isoformat()
                    if document.generated_at
                    else ""
                ),
            },
        }
    )


# =========================================================
# REGISTER COMPLAINT PDF ON BLOCKCHAIN
# =========================================================
@role_required("admin", "official")
@require_POST
def register_complaint_blockchain(
    request,
    document_id
):

    document = get_object_or_404(
        ComplaintDocument,
        document_id=document_id
    )

    fabric_document_id = (
        f"CMP-{document.complaint_id}"
    )

    recorded_by = str(
        request.session.get("username")
        or request.session.get("user_id")
        or "system"
    )

    try:

        # -------------------------------------------------
        # CHECK IF DOCUMENT ALREADY EXISTS ON FABRIC
        # -------------------------------------------------

        try:

            blockchain_document = get_document(
                fabric_document_id
            )

        except FabricServiceError:

            blockchain_document = None

        # -------------------------------------------------
        # ALREADY EXISTS ON FABRIC
        # -------------------------------------------------

        if blockchain_document:

            blockchain_hash = blockchain_document.get(
                "fileHash",
                ""
            )

            # Same Fabric ID but different hash
            if blockchain_hash != document.file_hash:

                document.blockchain_status = "Failed"

                document.save(
                    update_fields=[
                        "blockchain_status"
                    ]
                )

                create_blockchain_log(
                    blockchain_document_id=
                        fabric_document_id,
                    document_id=
                        document.document_id,
                    document_type="COMPLAINT",
                    document_hash=
                        document.file_hash,
                    transaction_hash=None,
                    action="REGISTER",
                    status="FAILED",
                    verification_status="Failed",
                    error_message=(
                        "Complaint document already "
                        "exists on Fabric with a "
                        "different hash."
                    ),
                    recorded_by=recorded_by,
                )

                return JsonResponse(
                    {
                        "success": False,
                        "error": (
                            "This complaint document "
                            "already exists on Fabric "
                            "with a different hash."
                        ),
                    },
                    status=409,
                )

            # Same Fabric ID + same hash
            document.blockchain_status = "Registered"

            if not document.blockchain_registered_at:
                document.blockchain_registered_at = (
                    timezone.now()
                )

            document.save(
                update_fields=[
                    "blockchain_status",
                    "blockchain_registered_at",
                ]
            )

            # This is an application audit entry.
            # No new Fabric transaction was created.
            create_blockchain_log(
                blockchain_document_id=
                    fabric_document_id,
                document_id=
                    document.document_id,
                document_type="COMPLAINT",
                document_hash=
                    document.file_hash,
                transaction_hash=
                    document.blockchain_tx_id,
                action="REGISTER",
                status="SUCCESS",
                verification_status="Pending",
                recorded_by=recorded_by,
            )

            return JsonResponse(
                {
                    "success": True,
                    "already_registered": True,
                    "document_id":
                        fabric_document_id,
                    "message": (
                        "Complaint document already "
                        "exists on Fabric and the "
                        "stored hash matches."
                    ),
                }
            )

        # -------------------------------------------------
        # NEW FABRIC REGISTRATION
        # -------------------------------------------------

        result = register_document(
            document_id=fabric_document_id,
            complaint_id=document.complaint_id,
            document_type="COMPLAINT",
            file_name=document.file_name,
            file_hash=document.file_hash,
            registered_by=recorded_by,
        )

        # -------------------------------------------------
        # UPDATE MYSQL
        # -------------------------------------------------

        document.blockchain_status = "Registered"

        document.blockchain_tx_id = result.get(
            "transactionId"
        )

        document.blockchain_registered_at = (
            timezone.now()
        )

        document.save(
            update_fields=[
                "blockchain_status",
                "blockchain_tx_id",
                "blockchain_registered_at",
            ]
        )

        # -------------------------------------------------
        # BLOCKCHAIN LOG - REGISTER SUCCESS
        # -------------------------------------------------

        create_blockchain_log(
            blockchain_document_id=
                fabric_document_id,
            document_id=
                document.document_id,
            document_type="COMPLAINT",
            document_hash=
                document.file_hash,
            transaction_hash=
                document.blockchain_tx_id,
            action="REGISTER",
            status="SUCCESS",
            verification_status="Pending",
            recorded_by=recorded_by,
        )

        return JsonResponse(
            {
                "success": True,
                "already_registered": False,
                "document_id":
                    fabric_document_id,
                "transaction_id":
                    document.blockchain_tx_id,
                "message": (
                    "Complaint PDF successfully "
                    "registered on Hyperledger Fabric."
                ),
            }
        )

    except FabricServiceError as error:

        document.blockchain_status = "Failed"

        document.save(
            update_fields=[
                "blockchain_status"
            ]
        )

        # -------------------------------------------------
        # BLOCKCHAIN LOG - REGISTER FAILED
        # -------------------------------------------------

        create_blockchain_log(
            blockchain_document_id=
                fabric_document_id,
            document_id=
                document.document_id,
            document_type="COMPLAINT",
            document_hash=
                document.file_hash,
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
# VERIFY COMPLAINT PDF INTEGRITY
# =========================================================
@role_required("admin", "official")
@require_POST
def verify_complaint_integrity(
    request,
    document_id
):

    document = get_object_or_404(
        ComplaintDocument,
        document_id=document_id
    )

    fabric_document_id = (
        f"CMP-{document.complaint_id}"
    )

    recorded_by = str(
        request.session.get("username")
        or request.session.get("user_id")
        or "system"
    )

    # Must be registered first
    if document.blockchain_status != "Registered":

        return JsonResponse(
            {
                "success": False,
                "error": (
                    "Complaint document must be "
                    "registered on Fabric before "
                    "verification."
                ),
            },
            status=400,
        )

    # File path required
    if not document.file_path:

        return JsonResponse(
            {
                "success": False,
                "error":
                    "Complaint PDF path is missing.",
            },
            status=400,
        )

    # -----------------------------------------------------
    # BUILD PHYSICAL FILE PATH
    # -----------------------------------------------------

    relative_path = (
        str(document.file_path)
        .replace("/media/", "", 1)
        .lstrip("/\\")
    )

    physical_path = os.path.join(
        settings.MEDIA_ROOT,
        relative_path
    )

    if not os.path.isfile(physical_path):

        return JsonResponse(
            {
                "success": False,
                "error":
                    "Complaint PDF could not be found.",
            },
            status=404,
        )

    try:

        # -------------------------------------------------
        # CALCULATE CURRENT PDF HASH
        # -------------------------------------------------

        current_hash = calculate_file_hash(
            physical_path
        )

        # -------------------------------------------------
        # VERIFY AGAINST FABRIC
        # -------------------------------------------------

        verified = verify_document(
            fabric_document_id,
            current_hash,
        )

        # -------------------------------------------------
        # UPDATE MYSQL
        # -------------------------------------------------

        document.last_verified_at = timezone.now()

        if verified:
            document.integrity_status = "Verified"
        else:
            document.integrity_status = "Failed"

        document.save(
            update_fields=[
                "integrity_status",
                "last_verified_at",
            ]
        )

        # -------------------------------------------------
        # BLOCKCHAIN LOG - VERIFY RESULT
        # -------------------------------------------------

        create_blockchain_log(
            blockchain_document_id=
                fabric_document_id,
            document_id=
                document.document_id,
            document_type="COMPLAINT",
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
                "document_id":
                    fabric_document_id,
                "verified":
                    verified,
                "integrity_status":
                    document.integrity_status,
                "current_hash":
                    current_hash,
                "last_verified_at":
                    document.last_verified_at.isoformat(),
            }
        )

    except FabricServiceError as error:

        # -------------------------------------------------
        # BLOCKCHAIN LOG - VERIFY ERROR
        # -------------------------------------------------

        create_blockchain_log(
            blockchain_document_id=
                fabric_document_id,
            document_id=
                document.document_id,
            document_type="COMPLAINT",
            document_hash=(
                current_hash
                if "current_hash" in locals()
                else document.file_hash
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