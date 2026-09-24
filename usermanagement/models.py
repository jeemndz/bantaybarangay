from django.db import models


class User(models.Model):

    ROLE_CHOICES = [
        ("resident", "Resident"),
        ("official", "Barangay Official"),
        ("admin", "Administrator"),
    ]

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
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
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
        managed = False
        db_table = "users"

    def __str__(self):
        return self.username