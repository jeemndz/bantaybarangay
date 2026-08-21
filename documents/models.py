from django.db import models
from registration.models import Resident


class Document(models.Model):

    document_id = models.AutoField(
        primary_key=True
    )

    resident = models.ForeignKey(
        Resident,
        db_column='resident_id',
        on_delete=models.DO_NOTHING,
        related_name='documents'
    )

    document_type = models.CharField(
        max_length=50
    )

    document_number = models.CharField(
        max_length=100
    )

    file_path = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )

    document_hash = models.CharField(
        max_length=64,
        null=True,
        blank=True
    )

    qr_code = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )

    issued_by = models.IntegerField(
        null=True,
        blank=True
    )

    issued_at = models.DateTimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=50
    )

    class Meta:
        db_table = 'documents'
        managed = False

    def __str__(self):
        return self.document_number