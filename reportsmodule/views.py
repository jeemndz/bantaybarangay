from django.shortcuts import render

# REPORTS & ANALYTICS

def reports(request):

    context = {

        # Summary Cards
        "monthly_complaints": 128,
        "incident_reports": 45,
        "resolution_rate": 94,
        "verified_documents": 2431,
        "officer_performance": 4.8,

    }


    return render(
        request,
        "reportsmodule/reports.html",
        context
    )