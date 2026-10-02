from django.db import models


# =====================================================
# RESIDENT
# =====================================================

class Resident(models.Model):

    resident_id = models.AutoField(
        primary_key=True
    )

    user_id = models.IntegerField(
        unique=True,
        blank=True,
        null=True
    )

    # =================================================
    # PERSONAL INFORMATION
    # =================================================

    first_name = models.CharField(
        max_length=100
    )

    middle_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    last_name = models.CharField(
        max_length=100
    )

    suffix = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    birth_date = models.DateField(
        blank=True,
        null=True
    )

    gender = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    civil_status = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    # =================================================
    # CONTACT INFORMATION
    # =================================================

    email = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    profile_picture_path = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    contact_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    # =================================================
    # ADDRESS
    # =================================================

    address = models.TextField(
        blank=True,
        null=True
    )

    house_block_lot = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    street_purok_sitio = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    province = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    municipality_city = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    barangay = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    zip_code = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    # =================================================
    # GOVERNMENT-ISSUED ID
    # =================================================

    id_type = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    id_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    id_file_path = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # =================================================
    # PROOF OF RESIDENCY
    # =================================================

    residency_document_type = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    residency_file_path = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # =================================================
    # VERIFICATION
    # =================================================

    verification_status = models.CharField(
        max_length=30,
        default="Pending"
    )

    verified_by = models.IntegerField(
        blank=True,
        null=True
    )

    verified_at = models.DateTimeField(
        blank=True,
        null=True
    )

    # =================================================
    # TIMESTAMPS
    # =================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # =================================================
    # MODEL CONFIGURATION
    # =================================================

    class Meta:
        db_table = "residents"
        managed = False

    def __str__(self):

        return (
            f"{self.first_name} "
            f"{self.last_name}"
        )