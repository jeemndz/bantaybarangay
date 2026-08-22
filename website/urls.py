from django.urls import path
from . import views

urlpatterns = [

    # Home
    path(
        "",
        views.home,
        name="home"
    ),

    # Submit Complaint
    path(
        "submit-complaint/",
        views.submit_complaint,
        name="submit_complaint"
    ),

    path("track-complaint/", views.track_complaint, name="track_complaint"),
    path("verify-document/", views.verify_document, name="verify_document"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
]