import os

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Document, DocumentType, ComplaintDocument
from registration.models import Resident

from evidencemodule.services.fabric_service import (
    FabricServiceError,
    register_document,
    get_document,
    verify_document,
)

from evidencemodule.services.hashing import calculate_file_hash


# =========================================================
# DOCUMENT LIST
# =========================================================

def document_list(request):

    # ==========================
    # GET ISSUED DOCUMENTS
    # ==========================

    documents = Document.objects.select_related(
        "document_type"
    ).all().order_by("-document_id")


    # ==========================
    # SEARCH
    # ==========================

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:
        documents = documents.filter(
            document_number__icontains=search
        )


    # ==========================
    # FILTER BY TYPE
    # ==========================

    selected_type = request.GET.get(
        "document_type",
        ""
    ).strip()

    if selected_type:
        documents = documents.filter(
            document_type__type_name=selected_type
        )


    # ==========================
    # FILTER BY STATUS
    # ==========================

    selected_status = request.GET.get(
        "status",
        ""
    ).strip()

    if selected_status:
        documents = documents.filter(
            status=selected_status
        )


    # ==========================
    # STATISTICS
    # ==========================

    total_documents = Document.objects.count()

    verified_documents = Document.objects.filter(
        status="Verified"
    ).count()

    pending_documents = Document.objects.filter(
        status="Pending"
    ).count()


    # ==========================
    # DOCUMENT TEMPLATES
    # ==========================

    document_types = DocumentType.objects.filter(
        status="Active"
    ).order_by("type_name")


    # ==========================
    # GET RESIDENTS
    # ==========================

    residents = Resident.objects.all()

    resident_dict = {
        resident.resident_id: resident
        for resident in residents
    }


    # ==========================
    # ATTACH RESIDENT
    # ==========================

    for document in documents:

        document.resident = resident_dict.get(
            document.resident_id
        )


    # ==========================
    # CONTEXT
    # ==========================

    context = {

        "documents": documents,

        # Used by DOCUMENT TEMPLATES
        "document_types": document_types,

        # Statistics
        "total_documents": total_documents,
        "verified_documents": verified_documents,
        "pending_documents": pending_documents,

        # Filters
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
# GET OFFICIAL COMPLAINT DOCUMENT
# =========================================================

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


    # =====================================================
    # BUILD FILE URL
    # =====================================================

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


    # =====================================================
    # RETURN DOCUMENT INFORMATION
    # =====================================================

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

@require_POST
def register_complaint_blockchain(request, document_id):

    document = get_object_or_404(
        ComplaintDocument,
        document_id=document_id
    )

    fabric_document_id = (
        f"CMP-{document.complaint_id}"
    )

    try:

        # =================================================
        # CHECK IF DOCUMENT ALREADY EXISTS ON FABRIC
        # =================================================

        try:

            blockchain_document = get_document(
                fabric_document_id
            )

        except FabricServiceError:

            blockchain_document = None


        # =================================================
        # ALREADY REGISTERED
        # =================================================

        if blockchain_document:

            blockchain_hash = (
                blockchain_document.get(
                    "fileHash",
                    ""
                )
            )

            # Same ID but different PDF/hash

            if blockchain_hash != document.file_hash:

                document.blockchain_status = (
                    "Failed"
                )

                document.save(
                    update_fields=[
                        "blockchain_status"
                    ]
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


            # Same document already exists

            document.blockchain_status = (
                "Registered"
            )

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

            return JsonResponse(
                {
                    "success": True,

                    "already_registered":
                        True,

                    "document_id":
                        fabric_document_id,

                    "message": (
                        "Complaint document already "
                        "exists on Fabric and the "
                        "stored hash matches."
                    ),
                }
            )


        # =================================================
        # NEW BLOCKCHAIN REGISTRATION
        # =================================================

        registered_by = (

            request.session.get(
                "username"
            )

            or request.session.get(
                "user_id"
            )

            or "system"
        )


        result = register_document(

            document_id=
                fabric_document_id,

            complaint_id=
                document.complaint_id,

            document_type=
                "COMPLAINT",

            file_name=
                document.file_name,

            file_hash=
                document.file_hash,

            registered_by=
                registered_by,

        )


        # =================================================
        # UPDATE MYSQL
        # =================================================

        document.blockchain_status = (
            "Registered"
        )

        document.blockchain_tx_id = (
            result.get(
                "transactionId"
            )
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


        return JsonResponse(
            {
                "success": True,

                "already_registered":
                    False,

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

        document.blockchain_status = (
            "Failed"
        )

        document.save(
            update_fields=[
                "blockchain_status"
            ]
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


    # =====================================================
    # MUST BE REGISTERED FIRST
    # =====================================================

    if (
        document.blockchain_status
        !=
        "Registered"
    ):

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


    # =====================================================
    # CHECK FILE PATH
    # =====================================================

    if not document.file_path:

        return JsonResponse(
            {
                "success": False,
                "error":
                    "Complaint PDF path is missing.",
            },
            status=400,
        )


    # =====================================================
    # BUILD PHYSICAL FILE PATH
    # =====================================================

    relative_path = (

        str(document.file_path)

        .replace(
            "/media/",
            "",
            1
        )

        .lstrip(
            "/\\"
        )
    )


    physical_path = os.path.join(
        settings.MEDIA_ROOT,
        relative_path
    )


    # =====================================================
    # CHECK PHYSICAL FILE
    # =====================================================

    if not os.path.isfile(
        physical_path
    ):

        return JsonResponse(
            {
                "success": False,

                "error":
                    "Complaint PDF could not be found.",
            },
            status=404,
        )


    try:

        # =================================================
        # HASH CURRENT PDF
        # =================================================

        current_hash = (
            calculate_file_hash(
                physical_path
            )
        )


        # =================================================
        # COMPARE AGAINST FABRIC
        # =================================================

        verified = verify_document(
            fabric_document_id,
            current_hash,
        )


        # =================================================
        # UPDATE MYSQL
        # =================================================

        document.last_verified_at = (
            timezone.now()
        )

        if verified:

            document.integrity_status = (
                "Verified"
            )

        else:

            document.integrity_status = (
                "Failed"
            )


        document.save(
            update_fields=[
                "integrity_status",
                "last_verified_at",
            ]
        )


        # =================================================
        # RETURN RESULT
        # =================================================

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

        return JsonResponse(
            {
                "success": False,
                "error": str(error),
            },
            status=502,
        )