from django.shortcuts import render

from .models import Document
from registration.models import Resident


def document_list(request):

    documents = Document.objects.all().order_by('-document_id')

    # ==========================
    # SEARCH
    # ==========================

    search = request.GET.get('search', '').strip()

    if search:
        documents = documents.filter(
            document_number__icontains=search
        )

    # ==========================
    # FILTER BY TYPE
    # ==========================

    document_type = request.GET.get(
        'document_type',
        ''
    )

    if document_type:
        documents = documents.filter(
            document_type=document_type
        )

    # ==========================
    # FILTER BY STATUS
    # ==========================

    status = request.GET.get(
        'status',
        ''
    )

    if status:
        documents = documents.filter(
            status=status
        )

    # ==========================
    # STATISTICS
    # ==========================

    total_documents = Document.objects.count()

    verified_documents = Document.objects.filter(
        status='Verified'
    ).count()

    pending_documents = Document.objects.filter(
        status='Pending'
    ).count()

    # ==========================
    # GET RESIDENTS
    # ==========================

    residents = Resident.objects.all()

    resident_dict = {
        resident.resident_id: resident
        for resident in residents
    }

    # Attach resident information
    for document in documents:

        document.resident = resident_dict.get(
            document.resident_id
        )

    # ==========================
    # CONTEXT
    # ==========================

    context = {

        'documents': documents,

        'total_documents':
            total_documents,

        'verified_documents':
            verified_documents,

        'pending_documents':
            pending_documents,

        'search':
            search,

        'selected_type':
            document_type,

        'selected_status':
            status,
    }

    return render(
        request,
        'documentmodule/document_list.html',
        context
    )