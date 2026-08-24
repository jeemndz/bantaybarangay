from django.db import models


class BlockchainLog(models.Model):

    id = models.BigAutoField(
        primary_key=True
    )

    document_id = models.IntegerField(
        null=True,
        blank=True
    )

    document_hash = models.CharField(
        max_length=64,
        null=True,
        blank=True
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

    block_number = models.BigIntegerField(
        null=True,
        blank=True
    )

    verification_status = models.CharField(
        max_length=30,
        null=True,
        blank=True
    )

    recorded_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'blockchain_logs'
        managed = False

    def __str__(self):
        return self.transaction_hash or str(self.id)