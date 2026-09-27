from django.urls import path

from . import views


# =========================================================
# URL PATTERNS
# =========================================================

urlpatterns = [

    # =====================================================
    # HOME
    # =====================================================

    path(
        "",
        views.home,
        name="home"
    ),

    # =====================================================
    # COMPLAINTS
    # =====================================================

    path(
        "submit-complaint/",
        views.submit_complaint,
        name="submit_complaint"
    ),

    path(
        "my-complaints/",
        views.my_complaints,
        name="my_complaints"
    ),

    path(
        "track-complaint/",
        views.track_complaint,
        name="track_complaint"
    ),

    # =====================================================
    # DOCUMENTS
    # =====================================================

    path(
        "request-document/",
        views.request_document,
        name="request_document"
    ),

    path(
        "verify-document/",
        views.verify_document,
        name="verify_document"
    ),

    # =====================================================
    # PROFILE
    # =====================================================

    path(
        "my_profile/",
        views.my_profile,
        name="my_profile"
    ),

    # =====================================================
    # GENERAL
    # =====================================================

    path(
        "about/",
        views.about,
        name="about"
    ),

    path(
        "contact/",
        views.contact,
        name="contact"
    ),

]