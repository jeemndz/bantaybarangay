from django.urls import path
from . import views


app_name = "evidencemodule"


urlpatterns = [

    # =====================================================
    # EVIDENCE MANAGEMENT
    # =====================================================

    path(
        "",
        views.evidence_list,
        name="evidence_list"
    ),


    # =====================================================
    # CREATE
    # =====================================================

    path(
        "create/",
        views.evidence_create,
        name="evidence_create"
    ),


    # =====================================================
    # EVIDENCE BELONGING TO COMPLAINT
    # =====================================================

    path(
        "complaint/<int:complaint_id>/",
        views.complaint_evidence,
        name="complaint_evidence"
    ),


    # =====================================================
    # DETAIL
    # =====================================================

    path(
        "<int:evidence_id>/",
        views.evidence_detail,
        name="evidence_detail"
    ),


    # =====================================================
    # DELETE
    # =====================================================

    path(
        "<int:evidence_id>/delete/",
        views.evidence_delete,
        name="evidence_delete"
    ),

]