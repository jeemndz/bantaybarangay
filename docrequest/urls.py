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

    path(
        "",
        views.document_request_list,
        name="request_documents"
    ),

]