from django.db import models


class Complaint(models.Model):

    complaint_id = models.AutoField(
        primary_key=True
    )

    resident_id = models.IntegerField()

    complaint_type = models.CharField(
        max_length=100
    )

    subject = models.CharField(
        max_length=255
    )

    description = models.TextField()

    location = models.TextField(
        null=True,
        blank=True
    )

    incident_date = models.DateTimeField(
        null=True,
        blank=True
    )

    priority = models.CharField(
        max_length=20
    )

    status = models.CharField(
        max_length=30
    )

    assigned_official = models.IntegerField(
        null=True,
        blank=True
    )

    resolution = models.TextField(
        null=True,
        blank=True
    )

    submitted_at = models.DateTimeField()

    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'complaints'
        managed = False

    def __str__(self):
        return f"Complaint #{self.complaint_id}"