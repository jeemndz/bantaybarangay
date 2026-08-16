from django.db import models


class User(models.Model):

    ROLE_CHOICES = [
        ('resident', 'Resident'),
        ('admin', 'Admin'),
        ('official', 'Official'),
    ]

    user_id = models.AutoField(
        primary_key=True
    )

    username = models.CharField(
        max_length=50
    )

    password_hash = models.CharField(
        max_length=255
    )

    email = models.CharField(
        max_length=100
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='resident'
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField()

    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'users'
        managed = False

    def __str__(self):
        return self.username