from django.shortcuts import render


def blockchain_logs(request):

    return render(
        request,
        "blockchain_logs/blockchain_logs.html"
    )