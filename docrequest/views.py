from django.shortcuts import render


def document_request_list(request):

    return render(
        request,
        "docrequest/document_request_list.html"
    )