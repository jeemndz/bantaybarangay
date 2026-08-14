from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from .models import Complaint
from .forms import ComplaintForm


def complaint_list(request):

    complaints = Complaint.objects.all().order_by('-complaint_id')

    search = request.GET.get('search', '')

    if search:
        complaints = complaints.filter(
            Q(subject__icontains=search) |
            Q(complaint_type__icontains=search) |
            Q(description__icontains=search) |
            Q(location__icontains=search)
        )

    status = request.GET.get('status', '')

    if status:
        complaints = complaints.filter(
            status=status
        )

    priority = request.GET.get('priority', '')

    if priority:
        complaints = complaints.filter(
            priority=priority
        )

    context = {
        'complaints': complaints,

        'total_filed': Complaint.objects.count(),

        'pending_action': Complaint.objects.filter(
            status__in=[
                'NEW',
                'UNDER_INVESTIGATION'
            ]
        ).count(),

        'resolved_this_month': Complaint.objects.filter(
            status='RESOLVED'
        ).count(),

        'avg_time_to_close': '3.2 Days',

        'search': search,

        'selected_status': status,

        'selected_priority': priority,
    }

    return render(
        request,
        'complaintmodule/complaints.html',
        context
    )


def complaint_create(request):

    if request.method == 'POST':

        form = ComplaintForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('complaint_list')

    else:

        form = ComplaintForm()

    context = {
        'form': form,
        'page_title': 'New Complaint',
        'page_description':
            'Register a new barangay complaint.'
    }

    return render(
        request,
        'complaintmodule/complaint_form.html',
        context
    )


def complaint_detail(request, complaint_id):

    complaint = get_object_or_404(
        Complaint,
        complaint_id=complaint_id
    )

    return render(
        request,
        'complaintmodule/complaint_detail.html',
        {
            'complaint': complaint
        }
    )


def complaint_update(request, complaint_id):

    complaint = get_object_or_404(
        Complaint,
        complaint_id=complaint_id
    )

    if request.method == 'POST':

        form = ComplaintForm(
            request.POST,
            instance=complaint
        )

        if form.is_valid():

            form.save()

            return redirect(
                'complaint_detail',
                complaint_id=complaint.complaint_id
            )

    else:

        form = ComplaintForm(
            instance=complaint
        )

    context = {
        'form': form,
        'complaint': complaint,
        'page_title': 'Edit Complaint',
        'page_description':
            'Update complaint information.'
    }

    return render(
        request,
        'complaintmodule/complaint_form.html',
        context
    )


def complaint_change_status(request, complaint_id):

    complaint = get_object_or_404(
        Complaint,
        complaint_id=complaint_id
    )

    if request.method == 'POST':

        new_status = request.POST.get('status')

        if new_status:

            complaint.status = new_status
            complaint.save(
                update_fields=[
                    'status',
                    'updated_at'
                ]
            )

    return redirect(
        'complaint_detail',
        complaint_id=complaint.complaint_id
    )


def complaint_delete(request, complaint_id):

    complaint = get_object_or_404(
        Complaint,
        complaint_id=complaint_id
    )

    if request.method == 'POST':

        complaint.delete()

        return redirect('complaint_list')

    return render(
        request,
        'complaintmodule/complaint_confirm_delete.html',
        {
            'complaint': complaint
        }
    )