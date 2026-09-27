from django.urls import path

from . import views


# =========================================================
# APP NAMESPACE
# =========================================================

app_name = "docrequestmodule"


# =========================================================
# URL PATTERNS
# =========================================================

urlpatterns = [

    # =====================================================
    # REQUEST LIST
    # =====================================================

    path(
        "",
        views.document_request_list,
        name="request_documents"
    ),

    # =====================================================
    # UPDATE STATUS
    # =====================================================

    path(
        "<int:request_id>/status/",
        views.update_request_status,
        name="update_request_status"
    ),

]