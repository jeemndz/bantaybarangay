from django.urls import path
from . import views


app_name = "docrequest"


urlpatterns = [

    path(
        "",
        views.document_request_list,
        name="document_request_list"
    ),

]