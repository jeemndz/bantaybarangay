from django.db import models


class AuditLog(models.Model):
    """
    Represents one system activity stored in the existing
    `audit_logs` database table.
    """

    audit_id = models.AutoField(
        primary_key=True,
        db_column="audit_id"
    )

    user_id = models.IntegerField(
        null=True,
        blank=True,
        db_column="user_id"
    )

    action = models.CharField(
        max_length=100,
        db_column="action"
    )

    module = models.CharField(
        max_length=100,
        db_column="module"
    )

    description = models.TextField(
        null=True,
        blank=True,
        db_column="description"
    )

    ip_address = models.CharField(
        max_length=45,
        null=True,
        blank=True,
        db_column="ip_address"
    )

    created_at = models.DateTimeField(
        db_column="created_at"
    )

    class Meta:
        db_table = "audit_logs"

        ordering = [
            "-created_at",
            "-audit_id",
        ]

        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

        # IMPORTANT:
        # Keep this False if the table already exists
        # in your database.
        managed = False

    def __str__(self):
        return (
            f"{self.module} - "
            f"{self.action} - "
            f"{self.created_at}"
        )