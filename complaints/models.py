from django.db import models


class Complaint(models.Model):

    resident_id = models.IntegerField()

    complaint_type = models.CharField(
        max_length=255
    )

    subject = models.CharField(
        max_length=255
    )

    description = models.TextField()

    location = models.TextField(
        blank=True,
        null=True
    )

    incident_date = models.DateTimeField(
        blank=True,
        null=True
    )

    priority = models.CharField(
        max_length=50
    )

    status = models.CharField(
        max_length=100,
        default="New"
    )

    submitted_at = models.DateTimeField(
        auto_now_add=False
    )

    updated_at = models.DateTimeField(
        auto_now=False
    )


    def __str__(self):

        return self.subject