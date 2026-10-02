from django.db import models


# =========================================================
# HEARING
# =========================================================

class Hearing(models.Model):

    # =====================================================
    # CHOICES
    # =====================================================

    SUMMONS_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Issued", "Issued"),
        ("Served", "Served"),
    ]

    HEARING_STAGE_CHOICES = [
        ("Mediation", "Mediation"),
        ("Conciliation", "Conciliation"),
        ("Pangkat", "Pangkat"),
        ("Arbitration", "Arbitration"),
        ("Settlement", "Settlement"),
    ]

    STATUS_CHOICES = [
        ("Scheduled", "Scheduled"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
        ("Postponed", "Postponed"),
        ("Cancelled", "Cancelled"),
    ]

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    hearing_id = models.AutoField(
        primary_key=True
    )

    # =====================================================
    # RELATED RECORD IDS
    # =====================================================

    resident_id = models.IntegerField()

    complaint_id = models.IntegerField()

    # =====================================================
    # CASE INFORMATION
    # =====================================================

    case_number = models.CharField(
        max_length=50
    )

    complainant_name = models.CharField(
        max_length=150
    )

    respondent_name = models.CharField(
        max_length=150
    )

    dispute_nature = models.CharField(
        max_length=150
    )

    # =====================================================
    # SCHEDULE
    # =====================================================

    hearing_date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    chamber = models.CharField(
        max_length=100
    )

    mediator = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )

    # =====================================================
    # SUMMONS
    # =====================================================

    summons_status = models.CharField(
        max_length=20,
        choices=SUMMONS_STATUS_CHOICES,
        default="Pending"
    )

    # =====================================================
    # HEARING STAGE
    # =====================================================

    hearing_stage = models.CharField(
        max_length=20,
        choices=HEARING_STAGE_CHOICES,
        default="Mediation"
    )

    # =====================================================
    # HEARING STATUS
    # =====================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Scheduled"
    )

    # =====================================================
    # NOTES
    # =====================================================

    notes = models.TextField(
        null=True,
        blank=True
    )

    # =====================================================
    # TIMESTAMPS
    # =====================================================

    created_at = models.DateTimeField(
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # =====================================================
    # META
    # =====================================================

    class Meta:
        db_table = "hearings"
        managed = False
        ordering = [
            "hearing_date",
            "start_time",
        ]

    # =====================================================
    # STRING
    # =====================================================

    def __str__(self):

        return (
            f"{self.case_number} - "
            f"{self.hearing_date}"
        )


# =========================================================
# HEARING ATTACHMENT
# =========================================================

class HearingAttachment(models.Model):

    # =====================================================
    # ATTACHMENT TYPES
    # =====================================================

    ATTACHMENT_TYPE_CHOICES = [
        (
            "Audio Recording",
            "Audio Recording"
        ),
        (
            "Document",
            "Document"
        ),
        (
            "Image",
            "Image"
        ),
        (
            "Hearing Minutes",
            "Hearing Minutes"
        ),
        (
            "Other",
            "Other"
        ),
    ]

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    attachment_id = models.AutoField(
        primary_key=True
    )

    # =====================================================
    # HEARING
    # =====================================================

    hearing = models.ForeignKey(
        Hearing,
        on_delete=models.CASCADE,
        db_column="hearing_id",
        related_name="attachments"
    )

    # =====================================================
    # ATTACHMENT TYPE
    # =====================================================

    attachment_type = models.CharField(
        max_length=30,
        choices=ATTACHMENT_TYPE_CHOICES,
        default="Document"
    )

    # =====================================================
    # FILE
    # =====================================================

    file = models.FileField(
        upload_to="hearing_attachments/"
    )

    # =====================================================
    # ORIGINAL FILE INFORMATION
    # =====================================================

    original_filename = models.CharField(
        max_length=255
    )

    file_type = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )

    file_size = models.BigIntegerField(
        default=0
    )

    # =====================================================
    # UPLOADED BY
    # =====================================================

    uploaded_by = models.IntegerField()

    # =====================================================
    # DESCRIPTION
    # =====================================================

    description = models.TextField(
        null=True,
        blank=True
    )

    # =====================================================
    # UPLOADED DATE
    # =====================================================

    uploaded_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # =====================================================
    # META
    # =====================================================

    class Meta:
        db_table = "hearing_attachments"
        managed = False
        ordering = [
            "-uploaded_at",
            "-attachment_id",
        ]

    # =====================================================
    # STRING
    # =====================================================

    def __str__(self):

        return (
            f"{self.original_filename} - "
            f"{self.hearing.case_number}"
        )

    # =====================================================
    # FILE EXTENSION
    # =====================================================

    @property
    def file_extension(self):

        if not self.original_filename:
            return ""

        if "." not in self.original_filename:
            return ""

        return (
            self.original_filename
            .rsplit(".", 1)[-1]
            .lower()
        )

    # =====================================================
    # IS AUDIO
    # =====================================================

    @property
    def is_audio(self):

        return self.file_extension in [
            "mp3",
            "wav",
            "ogg",
            "m4a",
            "aac",
        ]

    # =====================================================
    # IS IMAGE
    # =====================================================

    @property
    def is_image(self):

        return self.file_extension in [
            "jpg",
            "jpeg",
            "png",
            "gif",
            "webp",
        ]

    # =====================================================
    # IS DOCUMENT
    # =====================================================

    @property
    def is_document(self):

        return self.file_extension in [
            "pdf",
            "doc",
            "docx",
            "txt",
        ]

    # =====================================================
    # FORMATTED FILE SIZE
    # =====================================================

    @property
    def formatted_file_size(self):

        size = self.file_size or 0

        if size < 1024:

            return (
                f"{size} B"
            )

        if size < 1024 * 1024:

            return (
                f"{size / 1024:.1f} KB"
            )

        return (
            f"{size / (1024 * 1024):.1f} MB"
        )


# =========================================================
# HEARING MINUTES DOCUMENT
# =========================================================

class HearingMinutesDocument(models.Model):

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    document_id = models.AutoField(
        primary_key=True
    )

    # =====================================================
    # RELATED RECORD IDS
    # =====================================================

    hearing_id = models.IntegerField(
        db_index=True
    )

    complaint_id = models.IntegerField(
        db_index=True
    )

    # =====================================================
    # DOCUMENT INFORMATION
    # =====================================================

    document_type = models.CharField(
        max_length=50,
        default="HEARING_MINUTES"
    )

    file_name = models.CharField(
        max_length=255
    )

    file_path = models.CharField(
        max_length=500
    )

    file_hash = models.CharField(
        max_length=64
    )

    # =====================================================
    # BLOCKCHAIN REGISTRATION
    # =====================================================

    blockchain_status = models.CharField(
        max_length=20,
        default="Pending"
    )

    blockchain_tx_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    blockchain_registered_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # =====================================================
    # INTEGRITY VERIFICATION
    # =====================================================

    integrity_status = models.CharField(
        max_length=20,
        default="Not Verified"
    )

    last_verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # =====================================================
    # PROCESSED BY
    # =====================================================

    processed_by = models.IntegerField(
        null=True,
        blank=True
    )

    processed_by_name = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )

    processed_by_role = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    # =====================================================
    # TIMESTAMP
    # =====================================================

    generated_at = models.DateTimeField(
        auto_now_add=True
    )

    # =====================================================
    # META
    # =====================================================

    class Meta:
        db_table = "hearing_minutes_documents"
        ordering = [
            "-generated_at",
            "-document_id",
        ]

    # =====================================================
    # STRING
    # =====================================================

    def __str__(self):

        return (
            f"HRG-{self.hearing_id} - "
            f"{self.file_name}"
        )