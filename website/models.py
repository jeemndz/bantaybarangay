from django.db import models

from registration.models import Resident


# =========================================================
# COMPLAINT MODEL
# =========================================================

class Complaint(models.Model):

    # =====================================================
    # CHOICES
    # =====================================================

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


    # =====================================================
    # DATABASE FIELDS
    # =====================================================

    complaint_id = models.AutoField(
        primary_key=True
    )


    # -----------------------------------------------------
    # RESIDENT
    # -----------------------------------------------------

    resident = models.ForeignKey(
        Resident,
        models.DO_NOTHING,
        db_column="resident_id",
        related_name="complaints"
    )


    # -----------------------------------------------------
    # REPORT TYPE
    # -----------------------------------------------------

    report_type = models.CharField(
        max_length=30,
        choices=REPORT_TYPE_CHOICES,
        default="Formal Complaint"
    )


    # -----------------------------------------------------
    # COMPLAINT INFORMATION
    # -----------------------------------------------------

    complaint_type = models.CharField(
        max_length=100
    )

    subject = models.CharField(
        max_length=255
    )

    description = models.TextField()


    # -----------------------------------------------------
    # INCIDENT INFORMATION
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # RESPONDENT INFORMATION
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # COMPLAINT STATUS
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # ASSIGNED OFFICIAL
    # -----------------------------------------------------

    assigned_official = models.IntegerField(
        blank=True,
        null=True
    )


    # -----------------------------------------------------
    # RESOLUTION
    # -----------------------------------------------------

    resolution = models.TextField(
        blank=True,
        null=True
    )


    # -----------------------------------------------------
    # TIMESTAMPS
    # -----------------------------------------------------

    submitted_at = models.DateTimeField()

    updated_at = models.DateTimeField()


    # =====================================================
    # META
    # =====================================================

    class Meta:
        db_table = "complaints"
        managed = False
        ordering = ["-submitted_at"]


    # =====================================================
    # STRING REPRESENTATION
    # =====================================================

    def __str__(self):
        return f"{self.complaint_id} - {self.subject}"


    # =====================================================
    # REFERENCE NUMBER
    # =====================================================

    @property
    def reference_number(self):

        if self.submitted_at:
            year = self.submitted_at.year
        else:
            year = "0000"

        return f"CMP-{year}-{self.complaint_id:04d}"


    # =====================================================
    # STATUS GROUP
    # =====================================================

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


    # =====================================================
    # STATUS MESSAGE
    # =====================================================

    @property
    def latest_update(self):

        if self.resolution:
            return self.resolution

        messages = {

            "Submitted":
                "Your complaint has been submitted and is awaiting review.",

            "Under Review":
                "Your complaint is currently being reviewed by the barangay.",

            "Under Investigation":
                "Your complaint is currently under investigation.",

            "Resolved":
                "The complaint has been resolved.",

            "Rejected":
                "The complaint has been rejected.",

            "Closed":
                "The complaint has been officially closed.",
        }

        return messages.get(
            self.status,
            "Your complaint is currently being processed."
        )