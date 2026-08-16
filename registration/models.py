from django.db import models


class User(models.Model):

    user_id = models.AutoField(
        primary_key=True
    )

    username = models.CharField(
        max_length=50,
        unique=True
    )

    password_hash = models.CharField(
        max_length=255      
    )

    email = models.CharField(
        max_length=100
    )

    role = models.CharField(
        max_length=30,
        default='Resident'
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = 'users'
        managed = False


class Resident(models.Model):

    resident_id = models.AutoField(
        primary_key=True
    )

    user_id = models.IntegerField(
        unique=True
    )

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

    birth_date = models.DateField()

    gender = models.CharField(
        max_length=20
    )

    civil_status = models.CharField(
        max_length=30
    )

    address = models.TextField()

    contact_number = models.CharField(
        max_length=20
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
        max_length=100
    )

    municipality_city = models.CharField(
        max_length=100
    )

    barangay = models.CharField(
        max_length=100
    )

    zip_code = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    verification_status = models.CharField(
        max_length=30,
        default='Pending'
    )

    verified_by = models.IntegerField(
        blank=True,
        null=True
    )

    verified_at = models.DateTimeField(
        blank=True,
        null=True
    )

    email = models.CharField(
        max_length=100
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = 'residents'
        managed = False