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
    # RELEASE COMPLAINT DOCUMENTS
    # =====================================================

    path(
        "complaint/<int:complaint_id>/release-documents/",
        views.release_complaint_documents,
        name="release_complaint_documents"
    ),

    path(
        "my-complaints/"
        "<int:complaint_id>/"
        "document/"
        "<str:source>/"
        "<int:file_id>/",
        views.released_complaint_document,
        name="released_complaint_document"
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

    path(
        "my_profile/change-password/",
        views.change_password,
        name="change_password"
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