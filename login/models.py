from django.db import models

class User(models.Model):


    # ROLE CHOICES
    ROLE_CHOICES = [
        ("resident", "Resident"),
        ("official", "Official"),
        ("admin", "Admin"),
    ]

    # PRIMARY KEY
    user_id = models.AutoField(
        primary_key=True
    )

    # USERNAME
    username = models.CharField(
        max_length=50,
        unique=True
    )

    # PASSWORD
    password_hash = models.CharField(
        max_length=255
    )


    # EMAIL
    email = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    # ROLE
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )


    # ACCOUNT STATUS
    is_active = models.BooleanField(
        default=True,
        null=True
    )



    # TIMESTAMPS
    created_at = models.DateTimeField()

    updated_at = models.DateTimeField()


    # DATABASE CONFIGURATION
    class Meta:

        db_table = "users"

        # Existing MySQL table.
        # Django will not create, modify, or delete it.
        managed = False


    # STRING REPRESENTATION
    def __str__(self):

        return self.username


# PASSWORD RESET TOKEN MODEL
class PasswordResetToken(models.Model):


    # PRIMARY KEY
    reset_id = models.AutoField(
        primary_key=True
    )



    # USER
    user_id = models.IntegerField(
        db_index=True
    )


    # HASHED RESET TOKEN
    token_hash = models.CharField(
        max_length=64,
        unique=True
    )

    # EXPIRATION
    expires_at = models.DateTimeField()



    # TOKEN STATUS
    used = models.BooleanField(
        default=False
    )

    # CREATED DATE
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # DATABASE CONFIGURATION
    class Meta:

        db_table = "password_reset_tokens"

        # We created this table manually in MySQL.
        # Django should use it but not manage its schema.
        managed = False

    # STRING REPRESENTATION
    def __str__(self):

        return (
            f"Password reset token "
            f"for user {self.user_id}"
        )