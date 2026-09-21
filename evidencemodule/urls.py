from django.urls import path
from . import views


urlpatterns = [
    path(
        '',
        views.evidence_list,
        name='evidence_list'
    ),

    path(
        '<int:evidence_id>/',
        views.evidence_detail,
        name='evidence_detail'
    ),

    path(
        'create/',
        views.evidence_create,
        name='evidence_create'
    ),

    path(
        '<int:evidence_id>/delete/',
        views.evidence_delete,
        name='evidence_delete'
    ),
]