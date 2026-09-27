from django.urls import path
from . import views


app_name = "reportsmodule"


urlpatterns = [

    path(
        "",
        views.reports,
        name="reports"
    ),

]