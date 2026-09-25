from django.shortcuts import render

from .models import Document, DocumentType
from registration.models import Resident


def document_list(request):

    # ==========================
    # GET ISSUED DOCUMENTS
    # ==========================

    documents = Document.objects.select_related(
        'document_type'
    ).all().order_by('-document_id')


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

    selected_type = request.GET.get(
        'document_type',
        ''
    ).strip()

    if selected_type:
        documents = documents.filter(
            document_type__type_name=selected_type
        )


    # ==========================
    # FILTER BY STATUS
    # ==========================

    selected_status = request.GET.get(
        'status',
        ''
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
        status='Verified'
    ).count()

    pending_documents = Document.objects.filter(
        status='Pending'
    ).count()


    # ==========================
    # DOCUMENT TEMPLATES
    # ==========================

    document_types = DocumentType.objects.filter(
        status='Active'
    ).order_by('type_name')


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
        'documents': documents,

        # Used by DOCUMENT TEMPLATES
        'document_types': document_types,

        # Statistics
        'total_documents': total_documents,
        'verified_documents': verified_documents,
        'pending_documents': pending_documents,

        # Filters
        'search': search,
        'selected_type': selected_type,
        'selected_status': selected_status,
    }


    return render(
        request,
        'documentmodule/document_list.html',
        context
    )