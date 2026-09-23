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

    # Create
    path(
        "create/",
        views.evidence_create,
        name="evidence_create"
    ),

    # Detail
    path(
        "<int:evidence_id>/",
        views.evidence_detail,
        name="evidence_detail"
    ),

    # Delete
    path(
        "<int:evidence_id>/delete/",
        views.evidence_delete,
        name="evidence_delete"
    ),

]