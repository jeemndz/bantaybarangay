from django.db import connection


# =========================================================
# GET CLIENT IP
# =========================================================

def get_client_ip(request):
    """
    Get the IP address of the user making the request.
    """

    return request.META.get(
        "REMOTE_ADDR"
    )


# =========================================================
# CREATE AUDIT LOG
# =========================================================

def create_audit_log(
    request,
    action,
    module,
    description="",
    user_id=None
):
    """
    Create a new record in the audit_logs table.
    """

    # Use logged-in user's session ID when
    # user_id was not supplied manually.
    if user_id is None:

        user_id = request.session.get(
            "user_id"
        )


    ip_address = get_client_ip(
        request
    )


    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO audit_logs
                (
                    user_id,
                    action,
                    module,
                    description,
                    ip_address
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                [
                    user_id,
                    action,
                    module,
                    description or None,
                    ip_address,
                ]
            )

        return True


    except Exception as error:

        print(
            "AUDIT LOG ERROR:",
            error
        )

        return False