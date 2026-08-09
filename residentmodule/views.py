from django.shortcuts import render
from .models import Resident

# Create your views here.
def resident_list(request):
    residents = Resident.objects.all()

    context = {'residents': residents}

    return render(request, 'resident_list.html', context)


