from django.shortcuts import render


def hearing_schedule(request):
    return render(
        request,
        "hearingmodule/hearing_schedule.html"
    )