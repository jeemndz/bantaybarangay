from django.urls import path
from . import views


app_name = "documents"


urlpatterns = [

    # =====================================================
    # DOCUMENT MANAGEMENT
    # =====================================================

    path(
        "",
        views.document_list,
        name="document_list"
    ),


    # =====================================================
    # GET OFFICIAL COMPLAINT DOCUMENT
    # =====================================================

    path(
        "complaint/<int:complaint_id>/document/",
        views.complaint_document,
        name="complaint_document"
    ),


    # =====================================================
    # COMPLAINT PDF BLOCKCHAIN REGISTRATION
    # =====================================================

    path(
        "complaint/<int:document_id>/blockchain/register/",
        views.register_complaint_blockchain,
        name="register_complaint_blockchain"
    ),


    # =====================================================
    # COMPLAINT PDF INTEGRITY VERIFICATION
    # =====================================================

    path(
        "complaint/<int:document_id>/blockchain/verify/",
        views.verify_complaint_integrity,
        name="verify_complaint_integrity"
    ),

]