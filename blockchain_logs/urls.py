from django.urls import path
from . import views

urlpatterns = [
    path(
        "blockchain-logs/",
        views.blockchain_logs,
        name="blockchain_logs"
    ),
]