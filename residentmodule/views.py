from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Resident
from .forms import ResidentForm

def resident_list(request):

    residents = Resident.objects.all().order_by('-resident_id')

    verification_residents = Resident.objects.filter(
        verification_status='Pending'
    ).order_by('-resident_id')

    context = {
        'residents': residents,
        'verification_residents': verification_residents,
        'total_residents': residents.count(),
        'total_households': 0,
        'senior_citizens': 0,
        'pwd_residents': 0,
    }

    return render(
        request,
        'residentmodule/resident_list.html',
        context
    )
def resident_verify(request, resident_id):

    resident = get_object_or_404(
        Resident,
        resident_id=resident_id
    )

    if request.method == 'POST':

        action = request.POST.get('action')

        if action == 'verify':

            resident.verification_status = 'Verified'
            resident.verified_at = timezone.now()
            resident.verified_by = None

            resident.save(
                update_fields=[
                    'verification_status',
                    'verified_at',
                    'verified_by'
                ]
            )

            return redirect('resident_list')

        elif action == 'reject':

            resident.verification_status = 'Rejected'
            resident.verified_at = timezone.now()
            resident.verified_by = None

            resident.save(
                update_fields=[
                    'verification_status',
                    'verified_at',
                    'verified_by'
                ]
            )

            return redirect('resident_list')

    return render(
        request,
        'residentmodule/resident_verify.html',
        {
            'resident': resident
        }
    )

def resident_create(request):

    if request.method == 'POST':

        form = ResidentForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('resident_list')

    else:
        form = ResidentForm()

    context = {
        'form': form,
        'page_title': 'Add Resident',
        'page_description': 'Register a new resident in the barangay records.',
    }

    return render(
        request,
        'residentmodule/resident_form.html',
        context
    )

def resident_update(request, resident_id):

    resident = get_object_or_404(
        Resident,
        resident_id=resident_id
    )

    if request.method == 'POST':

        form = ResidentForm(
            request.POST,
            instance=resident
        )

        if form.is_valid():
            form.save()
            return redirect('resident_list')

    else:

        form = ResidentForm(
            instance=resident
        )

    context = {
        'form': form,
        'resident': resident,
        'page_title': 'Edit Resident',
        'page_description': 'Update the resident information.',
    }

    return render(
        request,
        'residentmodule/resident_form.html',
        context
    )

def resident_delete(request, resident_id):

    resident = get_object_or_404(
        Resident,
        resident_id=resident_id
    )

    if request.method == 'POST':

        resident.delete()

        return redirect('resident_list')

    return render(
        request,
        'residentmodule/resident_confirm_delete.html',
        {
            'resident': resident
        }
    )