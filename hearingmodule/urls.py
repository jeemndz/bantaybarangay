from django.urls import path

from . import views


app_name = "hearingmodule"


urlpatterns = [

    # =====================================================
    # HEARING PAGE
    # =====================================================

    path(
        "hearings/",
        views.hearing_schedule,
        name="hearing_schedule"
    ),


    # =====================================================
    # CREATE HEARING
    # =====================================================

    path(
        "hearings/create/",
        views.create_hearing,
        name="create_hearing"
    ),


    # =====================================================
    # START HEARING
    # =====================================================

    path(
        "hearings/<int:hearing_id>/start/",
        views.start_hearing,
        name="start_hearing"
    ),


    # =====================================================
    # COMPLETE HEARING
    # =====================================================

    path(
        "hearings/<int:hearing_id>/complete/",
        views.complete_hearing,
        name="complete_hearing"
    ),


    # =====================================================
    # POSTPONE HEARING
    # =====================================================

    path(
        "hearings/<int:hearing_id>/postpone/",
        views.postpone_hearing,
        name="postpone_hearing"
    ),


    # =====================================================
    # CANCEL HEARING
    # =====================================================

    path(
        "hearings/<int:hearing_id>/cancel/",
        views.cancel_hearing,
        name="cancel_hearing"
    ),


    # =====================================================
    # SAVE HEARING NOTES
    # =====================================================

    path(
        "hearings/<int:hearing_id>/notes/",
        views.save_hearing_notes,
        name="save_hearing_notes"
    ),


    # =====================================================
    # UPLOAD HEARING FILE
    # =====================================================

    path(
        "hearings/<int:hearing_id>/upload/",
        views.upload_hearing_attachment,
        name="upload_hearing_attachment"
    ),


    # =====================================================
    # DELETE HEARING FILE
    # =====================================================

    path(
        "hearings/attachments/<int:attachment_id>/delete/",
        views.delete_hearing_attachment,
        name="delete_hearing_attachment"
    ),
]