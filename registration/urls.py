from django.urls import path

from . import views


urlpatterns = [

    # STEP 1
    path(
        "",
        views.registration,
        name="registration"
    ),

    # STEP 2
    path(
        "contact/",
        views.step2_contact,
        name="step2_contact"
    ),

    # STEP 3
    path(
        "identity/",
        views.step3_identity,
        name="step3_identity"
    ),

    # STEP 4
    path(
        "review/",
        views.step4_review,
        name="step4_review"
    ),

    # SUCCESS
    path(
        "success/",
        views.registration_success,
        name="registration_success"
    ),

]