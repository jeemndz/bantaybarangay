from django.shortcuts import render, get_object_or_404

from .models import Document


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


# =====================================================
# DOCUMENT DETAIL
# =====================================================

def document_detail(request, document_id):

    document = get_object_or_404(
        Document,
        document_id=document_id
    )

    context = {
        'document': document
    }

    return render(
        request,
        'documentmodule/document_list.html',
        context
    )