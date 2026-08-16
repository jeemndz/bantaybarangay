from django.urls import path
from . import views


urlpatterns = [
    path(
        "",
        views.registration,
        name="registration"
    ),

    path(
        "contact/",
        views.step2_contact,
        name="step2_contact"
    ),
]