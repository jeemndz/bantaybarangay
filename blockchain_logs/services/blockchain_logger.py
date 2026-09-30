from django.utils import timezone

from blockchain_logs.models import BlockchainLog


def create_blockchain_log(
    *,
    blockchain_document_id,
    document_id,
    document_type,
    document_hash,
    transaction_hash=None,
    action=None,
    status=None,
    verification_status="Pending",
    error_message=None,
    recorded_by=None,
    block_number=None,
):
    """
    Creates a local audit log for a Hyperledger Fabric operation.
    """

    return BlockchainLog.objects.create(
        document_id=document_id,
        blockchain_document_id=blockchain_document_id,
        document_type=document_type,
        document_hash=document_hash,
        transaction_hash=transaction_hash,
        blockchain_network="Hyperledger Fabric",
        channel_name="mychannel",
        chaincode_name="documents",
        block_number=block_number,
        action=action,
        status=status,
        verification_status=verification_status,
        error_message=error_message,
        recorded_by=recorded_by,
        recorded_at=timezone.now(),
    )