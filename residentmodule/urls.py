from django.urls import path
from . import views


urlpatterns = [

    path(
        '',
        views.resident_list,
        name='resident_list'
    ),

    path(
        'add/',
        views.resident_create,
        name='resident_create'
    ),

    path(
        'edit/<int:resident_id>/',
        views.resident_update,
        name='resident_update'
    ),

    path(
        'delete/<int:resident_id>/',
        views.resident_delete,
        name='resident_delete'
    ),

]