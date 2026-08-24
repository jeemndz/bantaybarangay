from django.urls import path
from . import views


urlpatterns = [

    # ========================================================
    # RESIDENT LIST
    # ========================================================

    path(
        "",
        views.resident_list,
        name="resident_list"
    ),


    # ========================================================
    # RESIDENT VERIFICATION
    # ========================================================

    path(
        "verify/<int:resident_id>/",
        views.resident_verify,
        name="resident_verify"
    ),


    # ========================================================
    # ACCEPT RESIDENT
    # ========================================================

    path(
        "verify/<int:resident_id>/accept/",
        views.accept_resident,
        name="accept_resident"
    ),


    # ========================================================
    # REJECT RESIDENT
    # ========================================================

    path(
        "verify/<int:resident_id>/reject/",
        views.reject_resident,
        name="reject_resident"
    ),


    # ========================================================
    # CREATE
    # ========================================================

    path(
        "add/",
        views.resident_create,
        name="resident_create"
    ),


    # ========================================================
    # UPDATE
    # ========================================================

    path(
        "edit/<int:resident_id>/",
        views.resident_update,
        name="resident_update"
    ),


    # ========================================================
    # DELETE
    # ========================================================

    path(
        "delete/<int:resident_id>/",
        views.resident_delete,
        name="resident_delete"
    ),

]