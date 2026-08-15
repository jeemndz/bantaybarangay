from django.urls import path
from . import views

urlpatterns = [
    path("", views.complaints, name="complaints"),
    path("new/", views.new_complaint, name="new_complaint"),
]