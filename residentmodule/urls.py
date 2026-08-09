from django.urls import path
from . import views

urlpatterns = [
    path('residents/', views.resident_list, name='resident_list'),
]