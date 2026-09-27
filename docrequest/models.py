from django.db import models


# =========================================================
# DOCUMENT TYPE
# =========================================================

class DocumentType(models.Model):

    document_type_id = models.AutoField(
        primary_key=True
    )

    type_name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    file_path = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        default="Active"
    )

    created_at = models.DateTimeField()

    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "document_types"

    def __str__(self):
        return self.type_name


# =========================================================
# DOCUMENT REQUEST
# =========================================================

class DocumentRequest(models.Model):

    STATUS_CHOICES = [

        (
            "Submitted",
            "Submitted"
        ),

        (
            "Under Verification",
            "Under Verification"
        ),

        (
            "Ready for Signature",
            "Ready for Signature"
        ),

        (
            "Ready for Pickup",
            "Ready for Pickup"
        ),

        (
            "Released",
            "Released"
        ),

        (
            "Rejected",
            "Rejected"
        ),

        (
            "Cancelled",
            "Cancelled"
        ),

    ]

    request_id = models.AutoField(
        primary_key=True
    )

    resident_id = models.IntegerField()

    document_type = models.ForeignKey(
        DocumentType,
        models.DO_NOTHING,
        db_column="document_type_id",
        related_name="requests"
    )

    purpose = models.CharField(
        max_length=255
    )

    institution = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    request_notes = models.TextField(
        blank=True,
        null=True
    )

    delivery_method = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    payment_method = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="Submitted"
    )

    submitted_at = models.DateTimeField()

    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "document_requests"
        ordering = [
            "-submitted_at"
        ]

    def __str__(self):
        return self.reference_number

    @property
    def reference_number(self):

        if self.submitted_at:
            year = self.submitted_at.year
        else:
            year = "0000"

        return (
            f"DOC-{year}-"
            f"{self.request_id:04d}"
        )