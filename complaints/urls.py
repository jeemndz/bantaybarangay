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

    path(
    "complaint/<int:complaint_id>/verified-files/",
    views.verified_complaint_files,
    name="verified_complaint_files"
),

path(
    "complaint/<int:complaint_id>/release-documents/",
    views.release_complaint_documents,
    name="release_complaint_documents",
),

]