from django.shortcuts import render


def home(request):
    return render(request, "website/home.html")


def submit_complaint(request):
    return render(request, "website/submit_complaint.html")


def track_complaint(request):
    return render(request, "website/track_complaint.html")


def verify_document(request):
    return render(request, "website/verify_document.html")


def about(request):
    return render(request, "website/about.html")


def contact(request):
    return render(request, "website/contact.html")