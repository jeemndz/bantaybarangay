import requests


FABRIC_GATEWAY_URL = "http://localhost:3001"


class FabricServiceError(Exception):
    """Raised when communication with the Fabric Gateway fails."""
    pass


def register_document(
    document_id,
    complaint_id,
    document_type,
    file_name,
    file_hash,
    registered_by,
):
    """
    Register a document hash on Hyperledger Fabric.
    """

    url = f"{FABRIC_GATEWAY_URL}/api/documents/register"

    payload = {
        "documentId": str(document_id),
        "complaintId": str(complaint_id),
        "documentType": str(document_type),
        "fileName": str(file_name),
        "fileHash": str(file_hash),
        "registeredBy": str(registered_by),
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=15,
        )

        data = response.json()

    except requests.RequestException as exc:
        raise FabricServiceError(
            f"Unable to connect to Fabric Gateway: {exc}"
        ) from exc

    except ValueError as exc:
        raise FabricServiceError(
            "Fabric Gateway returned an invalid response."
        ) from exc

    if not response.ok or not data.get("success"):
        raise FabricServiceError(
            data.get(
                "error",
                "Fabric document registration failed.",
            )
        )

    return data


def get_document(document_id):
    """
    Retrieve a registered document from Hyperledger Fabric.
    """

    url = (
        f"{FABRIC_GATEWAY_URL}/api/documents/"
        f"{document_id}"
    )

    try:
        response = requests.get(
            url,
            timeout=15,
        )

        data = response.json()

    except requests.RequestException as exc:
        raise FabricServiceError(
            f"Unable to connect to Fabric Gateway: {exc}"
        ) from exc

    except ValueError as exc:
        raise FabricServiceError(
            "Fabric Gateway returned an invalid response."
        ) from exc

    if not response.ok or not data.get("success"):
        raise FabricServiceError(
            data.get(
                "error",
                "Unable to retrieve document from Fabric.",
            )
        )

    return data.get("document")


def verify_document(
    document_id,
    file_hash,
):
    """
    Compare a file hash with the hash registered on Fabric.
    """

    url = f"{FABRIC_GATEWAY_URL}/api/documents/verify"

    payload = {
        "documentId": str(document_id),
        "fileHash": str(file_hash),
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=15,
        )

        data = response.json()

    except requests.RequestException as exc:
        raise FabricServiceError(
            f"Unable to connect to Fabric Gateway: {exc}"
        ) from exc

    except ValueError as exc:
        raise FabricServiceError(
            "Fabric Gateway returned an invalid response."
        ) from exc

    if not response.ok or not data.get("success"):
        raise FabricServiceError(
            data.get(
                "error",
                "Fabric document verification failed.",
            )
        )

    return bool(
        data.get("verified")
    )