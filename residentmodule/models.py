from django.db import models


class Resident(models.Model):

    resident_id = models.AutoField(
        primary_key=True
    )

    user_id = models.IntegerField(
        null=True,
        blank=True,
        unique=True
    )

    first_name = models.CharField(
        max_length=100
    )

    middle_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    last_name = models.CharField(
        max_length=100
    )

    suffix = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    birth_date = models.DateField(
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=10,
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other'),
        ],
        null=True,
        blank=True
    )

    address = models.TextField()

    contact_number = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    email = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    # ---------------------------------------------
    # VERIFICATION
    # ---------------------------------------------

    verification_status = models.CharField(
        max_length=30,
        default='Pending'
    )

    verified_by = models.IntegerField(
        null=True,
        blank=True
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = 'residents'
        managed = False

    def __str__(self):
        return f"{self.first_name} {self.last_name}"