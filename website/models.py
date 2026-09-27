from django.db import models

from registration.models import Resident


# =========================================================
# COMPLAINT MODEL
# =========================================================

class Complaint(models.Model):

    PRIORITY_CHOICES = [
        ("N/A", "N/A"),
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
        ("Urgent", "Urgent"),
    ]

    STATUS_CHOICES = [
        ("Submitted", "Submitted"),
        ("Under Review", "Under Review"),
        ("Under Investigation", "Under Investigation"),
        ("Resolved", "Resolved"),
        ("Rejected", "Rejected"),
        ("Closed", "Closed"),
    ]

    REPORT_TYPE_CHOICES = [
        ("Formal Complaint", "Formal Complaint"),
        ("Community Issue", "Community Issue"),
    ]

    complaint_id = models.AutoField(
        primary_key=True
    )

    resident = models.ForeignKey(
        Resident,
        models.DO_NOTHING,
        db_column="resident_id",
        related_name="complaints"
    )

    report_type = models.CharField(
        max_length=30,
        choices=REPORT_TYPE_CHOICES,
        default="Formal Complaint"
    )

    complaint_type = models.CharField(
        max_length=100
    )

    subject = models.CharField(
        max_length=255
    )

    description = models.TextField()

    location = models.TextField(
        blank=True,
        null=True
    )

    incident_date = models.DateField(
        blank=True,
        null=True
    )

    incident_time = models.TimeField(
        blank=True,
        null=True
    )

    respondent_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    respondent_address = models.TextField(
        blank=True,
        null=True
    )

    respondent_relationship = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    respondent_contact = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="N/A"
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="Submitted"
    )

    assigned_official = models.IntegerField(
        blank=True,
        null=True
    )

    resolution = models.TextField(
        blank=True,
        null=True
    )

    submitted_at = models.DateTimeField()

    updated_at = models.DateTimeField()

    class Meta:
        db_table = "complaints"
        managed = False
        ordering = ["-submitted_at"]

    def __str__(self):
        return (
            f"{self.complaint_id} - "
            f"{self.subject}"
        )

    @property
    def reference_number(self):

        if self.submitted_at:
            year = self.submitted_at.year
        else:
            year = "0000"

        return (
            f"CMP-{year}-"
            f"{self.complaint_id:04d}"
        )

    @property
    def status_group(self):

        if self.status in [
            "Submitted",
            "Under Review",
            "Under Investigation",
        ]:
            return "progress"

        if self.status in [
            "Resolved",
            "Closed",
        ]:
            return "resolved"

        if self.status == "Rejected":
            return "rejected"

        return "progress"

    @property
    def latest_update(self):

        if self.resolution:
            return self.resolution

        messages = {

            "Submitted":
                "Your complaint has been submitted "
                "and is awaiting review.",

            "Under Review":
                "Your complaint is currently being "
                "reviewed by the barangay.",

            "Under Investigation":
                "Your complaint is currently under "
                "investigation.",

            "Resolved":
                "The complaint has been resolved.",

            "Rejected":
                "The complaint has been rejected.",

            "Closed":
                "The complaint has been officially "
                "closed.",
        }

        return messages.get(
            self.status,
            "Your complaint is currently being processed."
        )


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
        db_table = "document_types"
        managed = False
        ordering = ["type_name"]

    def __str__(self):
        return self.type_name


# =========================================================
# DOCUMENT REQUEST
# =========================================================

class DocumentRequest(models.Model):

    STATUS_CHOICES = [
        ("Submitted", "Submitted"),
        ("Under Verification", "Under Verification"),
        ("Ready for Signature", "Ready for Signature"),
        ("Ready for Pickup", "Ready for Pickup"),
        ("Released", "Released"),
        ("Rejected", "Rejected"),
        ("Cancelled", "Cancelled"),
    ]

    request_id = models.AutoField(
        primary_key=True
    )

    resident = models.ForeignKey(
        Resident,
        models.DO_NOTHING,
        db_column="resident_id",
        related_name="document_requests"
    )

    document_type = models.ForeignKey(
        DocumentType,
        models.DO_NOTHING,
        db_column="document_type_id",
        related_name="document_requests"
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
        db_table = "document_requests"
        managed = False
        ordering = ["-submitted_at"]

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

    @property
    def document_name(self):
        return self.document_type.type_name

    @property
    def created_at(self):
        return self.submitted_at