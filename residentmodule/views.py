from django.shortcuts import render
from .models import Resident


def resident_list(request):
    residents = Resident.objects.all()

    context = {
        'residentsAll': residents
    }

    return render(
        request,
        'residentmodule/resident_list.html',
        context
    )