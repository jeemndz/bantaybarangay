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
    # BLOCKCHAIN REGISTRATION
    # =====================================================

    path(
        "<int:evidence_id>/blockchain/register/",
        views.register_evidence_blockchain,
        name="register_evidence_blockchain"
    ),


    # =====================================================
    # BLOCKCHAIN INTEGRITY VERIFICATION
    # =====================================================

    path(
        "<int:evidence_id>/blockchain/verify/",
        views.verify_evidence_integrity,
        name="verify_evidence_integrity"
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