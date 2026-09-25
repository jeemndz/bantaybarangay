from django.db import models


class Complaint(models.Model):

    # =====================================================
    # CHOICES
    # =====================================================

    REPORT_TYPE_CHOICES = [
        ("Formal Complaint", "Formal Complaint"),
        ("Community Issue", "Community Issue"),
    ]

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


    # =====================================================
    # PRIMARY KEY
    # =====================================================

    complaint_id = models.AutoField(
        primary_key=True
    )


    # =====================================================
    # RESIDENT
    # =====================================================

    resident_id = models.IntegerField()


    # =====================================================
    # REPORT TYPE
    # =====================================================

    report_type = models.CharField(
        max_length=30,
        choices=REPORT_TYPE_CHOICES,
        default="Formal Complaint"
    )


    # =====================================================
    # COMPLAINT INFORMATION
    # =====================================================

    complaint_type = models.CharField(
        max_length=100
    )

    subject = models.CharField(
        max_length=255
    )

    description = models.TextField()


    # =====================================================
    # INCIDENT INFORMATION
    # =====================================================

    location = models.TextField(
        null=True,
        blank=True
    )

    incident_date = models.DateField(
        null=True,
        blank=True
    )

    incident_time = models.TimeField(
        null=True,
        blank=True
    )


    # =====================================================
    # RESPONDENT INFORMATION
    # =====================================================

    respondent_name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    respondent_address = models.TextField(
        null=True,
        blank=True
    )

    respondent_relationship = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    respondent_contact = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )


    # =====================================================
    # PRIORITY
    # =====================================================

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="N/A"
    )


    # =====================================================
    # STATUS
    # =====================================================

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="Submitted"
    )


    # =====================================================
    # ASSIGNED OFFICIAL
    # =====================================================

    assigned_official = models.IntegerField(
        null=True,
        blank=True
    )


    # =====================================================
    # RESOLUTION
    # =====================================================

    resolution = models.TextField(
        null=True,
        blank=True
    )


    # =====================================================
    # TIMESTAMPS
    # =====================================================

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
    # STRING
    # =====================================================

    def __str__(self):
        return f"Complaint #{self.complaint_id} - {self.subject}"


    # =====================================================
    # REFERENCE NUMBER
    # =====================================================

    @property
    def reference_number(self):

        if self.submitted_at:
            year = self.submitted_at.year
        else:
            year = "0000"

        return f"CP-{year}-{self.complaint_id:04d}"


    # =====================================================
    # WORKFLOW GROUP
    # =====================================================

    @property
    def workflow_group(self):

        if self.status in [
            "Submitted",
            "Under Review",
        ]:
            return "new"

        if self.status == "Under Investigation":
            return "ongoing"

        if self.status in [
            "Resolved",
            "Rejected",
            "Closed",
        ]:
            return "completed"

        return "new"