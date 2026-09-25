from django.urls import path
from . import views

app_name = "hearingmodule"

urlpatterns = [
    path(
        "hearings/",
        views.hearing_schedule,
        name="hearing_schedule"
    ),
]