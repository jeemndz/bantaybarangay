from django.shortcuts import render


# =========================================================
# DOCUMENT REQUEST LIST
# =========================================================

def document_request_list(request):

    return render(
        request,
        "docrequestmodule/request_documents.html"
    )