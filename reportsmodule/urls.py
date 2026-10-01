from django.urls import path
from . import views


app_name = "reportsmodule"


urlpatterns = [

    path(
        "",
        views.reports,
        name="reports"
    ),

    path(
        "export/pdf/",
        views.export_reports_pdf,
        name="export_pdf"
    ),

    path(
        "export/excel/",
        views.export_reports_excel,
        name="export_excel"
    ),

]