from django.db import models


class AuditLog(models.Model):
    """
    Represents one system activity stored in the existing
    `audit_logs` database table.
    """

    # =====================================================
    # ACTION CONSTANTS
    # =====================================================

    ACTION_LOGIN = "LOGIN"
    ACTION_LOGOUT = "LOGOUT"
    ACTION_CREATE = "CREATE"
    ACTION_UPDATE = "UPDATE"
    ACTION_DELETE = "DELETE"
    ACTION_APPROVE = "APPROVE"
    ACTION_REJECT = "REJECT"
    ACTION_VERIFY = "VERIFY"
    ACTION_UPLOAD = "UPLOAD"
    ACTION_DOWNLOAD = "DOWNLOAD"
    ACTION_RELEASE = "RELEASE"
    ACTION_CANCEL = "CANCEL"
    ACTION_VIEW = "VIEW"

    # =====================================================
    # MODULE CONSTANTS
    # =====================================================

    MODULE_AUTHENTICATION = "Authentication"
    MODULE_RESIDENTS = "Residents"
    MODULE_COMPLAINTS = "Complaints"
    MODULE_HEARINGS = "Hearings"
    MODULE_DOCUMENT_REQUESTS = "Document Requests"
    MODULE_DOCUMENTS = "Documents"
    MODULE_EVIDENCE = "Evidence"
    MODULE_USER_MANAGEMENT = "User Management"
    MODULE_AUDIT_LOGS = "Audit Logs"

    # =====================================================
    # DATABASE FIELDS
    # =====================================================

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

    # =====================================================
    # META
    # =====================================================

    class Meta:
        db_table = "audit_logs"

        managed = False

        ordering = [
            "-created_at",
            "-audit_id",
        ]

        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    # =====================================================
    # STRING REPRESENTATION
    # =====================================================

    def __str__(self):
        return (
            f"{self.module} - "
            f"{self.action} - "
            f"{self.created_at}"
        )