from django.db import models


class Evidence(models.Model):

    # =====================================================
    # CHOICES
    # =====================================================

    BLOCKCHAIN_STATUS_CHOICES = [
        ("Pending", "Pending Registration"),
        ("Registered", "Registered"),
        ("Failed", "Registration Failed"),
    ]

    INTEGRITY_STATUS_CHOICES = [
        ("Not Verified", "Not Verified"),
        ("Verified", "Verified"),
        ("Failed", "Integrity Check Failed"),
    ]


    # =====================================================
    # PRIMARY KEY
    # =====================================================

    evidence_id = models.AutoField(
        primary_key=True
    )


    # =====================================================
    # COMPLAINT
    # =====================================================

    # Complaint this evidence belongs to
    complaint_id = models.IntegerField(
        db_index=True
    )


    # =====================================================
    # UPLOADER
    # =====================================================

    # User who uploaded the evidence
    uploaded_by = models.IntegerField()


    # =====================================================
    # FILE INFORMATION
    # =====================================================

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


    # =====================================================
    # SHA-256 HASH
    # =====================================================

    file_hash = models.CharField(
        max_length=64
    )


    # =====================================================
    # BLOCKCHAIN REGISTRATION
    # =====================================================

    blockchain_status = models.CharField(
        max_length=20,
        choices=BLOCKCHAIN_STATUS_CHOICES,
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
        choices=INTEGRITY_STATUS_CHOICES,
        default="Not Verified"
    )

    last_verified_at = models.DateTimeField(
        null=True,
        blank=True
    )


    # =====================================================
    # TIMESTAMP
    # =====================================================

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )


    # =====================================================
    # META
    # =====================================================

    class Meta:
        db_table = "evidence"


    # =====================================================
    # STRING
    # =====================================================

    def __str__(self):
        return self.file_name