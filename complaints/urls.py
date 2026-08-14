from django.urls import path

from . import views


urlpatterns = [

    path(
        "complaints/",
        views.complaints,
        name="complaints"
    ),

    path(
        "complaints/new/",
        views.new_complaint,
        name="new_complaint"
    ),

]