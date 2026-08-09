from django.shortcuts import render
from .models import Resident

# Create your views here.
def resident_list(request):
    residents = Resident.objects.all() # for returning all residents from the database

    context = {'residents': residents}

    return render(request, 'resident_list.html', context) # for rendering the resident_list.html template with the residents data
