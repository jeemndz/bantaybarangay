from django.db import models


class Evidence(models.Model):

    evidence_id = models.AutoField(
        primary_key=True
    )

    # Complaint this evidence belongs to
    complaint_id = models.IntegerField(
        db_index=True
    )

    # User who uploaded the evidence
    uploaded_by = models.IntegerField()

    file_name = models.CharField(
        max_length=255
    )

    file_path = models.CharField(
        max_length=500
    )

    file_type = models.CharField(
        max_length=100
    )

    file_size = models.BigIntegerField()

    file_hash = models.CharField(
        max_length=64
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "evidence"

    def __str__(self):
        return self.file_name