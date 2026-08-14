from django.urls import path
from . import views


urlpatterns = [

    path(
        '',
        views.complaint_list,
        name='complaint_list'
    ),

    path(
        'add/',
        views.complaint_create,
        name='complaint_create'
    ),

    path(
        '<int:complaint_id>/',
        views.complaint_detail,
        name='complaint_detail'
    ),

    path(
        '<int:complaint_id>/edit/',
        views.complaint_update,
        name='complaint_update'
    ),

    path(
        '<int:complaint_id>/status/',
        views.complaint_change_status,
        name='complaint_change_status'
    ),

    path(
        '<int:complaint_id>/delete/',
        views.complaint_delete,
        name='complaint_delete'
    ),
]