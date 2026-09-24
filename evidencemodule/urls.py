from django.urls import path
from . import views


app_name = "evidencemodule"


urlpatterns = [

    # Evidence Management
    path(
        "",
        views.evidence_list,
        name="evidence_list"
    ),

    # Create Evidence
    path(
        "create/",
        views.evidence_create,
        name="evidence_create"
    ),

    # Get Complaints for Selected Resident
    path(
        "resident/<int:resident_id>/complaints/",
        views.resident_complaints,
        name="resident_complaints"
    ),

    # Evidence Detail
    path(
        "<int:evidence_id>/",
        views.evidence_detail,
        name="evidence_detail"
    ),

    # Delete Evidence
    path(
        "<int:evidence_id>/delete/",
        views.evidence_delete,
        name="evidence_delete"
    ),

]