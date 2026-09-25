from django.urls import path
from . import views

urlpatterns = [


    path(
        "",
        views.complaints,
        name="complaints"
    ),


    path(
        "new/",
        views.new_complaint,
        name="new_complaint"
    ),


    path(
        "<int:complaint_id>/update/",
        views.update_complaint,
        name="update_complaint"
    ),

]