from django.db import models


class BlockchainLog(models.Model):

    ACTION_CHOICES = [
        ("REGISTER", "Register"),
        ("VERIFY", "Verify"),
        ("QUERY", "Query"),
    ]

    STATUS_CHOICES = [
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    VERIFICATION_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Failed", "Failed"),
    ]

    blockchain_log_id = models.AutoField(
        primary_key=True
    )

    document_id = models.IntegerField()

    blockchain_document_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    document_type = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    document_hash = models.CharField(
        max_length=64
    )

    transaction_hash = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    blockchain_network = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    channel_name = models.CharField(
        max_length=100,
        default="mychannel"
    )

    chaincode_name = models.CharField(
        max_length=100,
        default="documents"
    )

    block_number = models.BigIntegerField(
        null=True,
        blank=True
    )

    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        null=True,
        blank=True
    )

    verification_status = models.CharField(
        max_length=30,
        choices=VERIFICATION_STATUS_CHOICES,
        default="Pending",
        null=True,
        blank=True
    )

    error_message = models.TextField(
        null=True,
        blank=True
    )

    recorded_by = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )

    recorded_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        db_table = "blockchain_logs"
        managed = False
        ordering = ["-recorded_at"]

    def __str__(self):
        return (
            self.transaction_hash
            or self.blockchain_document_id
            or str(self.blockchain_log_id)
        )