from django.contrib import messages
from django.db import connection, transaction
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from bantaybarangay.security import role_required

# =========================================================
# STATUS CHOICES
# =========================================================

DOCUMENT_REQUEST_STATUSES = [
    "Submitted",
    "Under Verification",
    "Ready for Signature",
    "Ready for Pickup",
    "Released",
    "Rejected",
    "Cancelled",
]


# =========================================================
# DOCUMENT REQUEST LIST
# =========================================================
@role_required("admin", "official")
def document_request_list(request):

    document_requests = []

    # =====================================================
    # FILTER VALUES
    # =====================================================

    search = (
        request.GET.get("search", "")
        .strip()
    )

    status_filter = (
        request.GET.get("status", "")
        .strip()
    )

    document_filter = (
        request.GET.get("document_type", "")
        .strip()
    )

    # =====================================================
    # LOAD DOCUMENT TYPES
    # =====================================================

    document_types = []

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    document_type_id,
                    type_name

                FROM document_types

                WHERE status = 'Active'

                ORDER BY type_name ASC
                """
            )

            type_rows = cursor.fetchall()

        for row in type_rows:

            document_types.append({

                "document_type_id":
                    row[0],

                "type_name":
                    row[1],
            })

    except Exception as e:

        print(
            "DOCUMENT TYPES ERROR:",
            e
        )

    # =====================================================
    # BUILD QUERY
    # =====================================================

    query = """
        SELECT
            dr.request_id,
            dr.reference_number,
            dr.resident_id,

            r.first_name,
            r.middle_name,
            r.last_name,
            r.suffix,

            r.address,
            r.email,
            r.contact_number,

            dt.document_type_id,
            dt.type_name,

            dr.purpose,
            dr.institution,
            dr.request_notes,

            dr.delivery_method,
            dr.payment_method,

            dr.status,
            dr.created_at,
            dr.updated_at

        FROM document_requests dr

        INNER JOIN document_types dt
            ON dt.document_type_id =
               dr.document_type_id

        INNER JOIN residents r
            ON r.resident_id =
               dr.resident_id

        WHERE 1 = 1
    """

    parameters = []

    # =====================================================
    # STATUS FILTER
    # =====================================================

    if status_filter:

        query += """
            AND dr.status = %s
        """

        parameters.append(
            status_filter
        )

    # =====================================================
    # DOCUMENT TYPE FILTER
    # =====================================================

    if document_filter:

        query += """
            AND dr.document_type_id = %s
        """

        parameters.append(
            document_filter
        )

    # =====================================================
    # SEARCH
    # =====================================================

    if search:

        query += """
            AND (
                r.first_name LIKE %s
                OR r.middle_name LIKE %s
                OR r.last_name LIKE %s
                OR dt.type_name LIKE %s
                OR dr.purpose LIKE %s
                OR dr.institution LIKE %s
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
        ])

    # =====================================================
    # ORDER
    # =====================================================

    query += """
        ORDER BY
            dr.created_at DESC
    """

    # =====================================================
    # EXECUTE QUERY
    # =====================================================

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                parameters
            )

            rows = cursor.fetchall()

        # =================================================
        # CONVERT ROWS
        # =================================================

        for row in rows:

            # =============================================
            # RESIDENT NAME
            # =============================================

            name_parts = [
                row[3],  # first_name
                row[4],  # middle_name
                row[5],  # last_name
                row[6],  # suffix
            ]

            resident_name = " ".join(
                str(part).strip()
                for part in name_parts
                if part and str(part).strip()
            )

            # =============================================
            # ADD REQUEST
            # =============================================

            document_requests.append({

                "request_id":
                    row[0],

                "reference_number":
                    row[1],

                "resident_id":
                    row[2],

                "resident_name":
                    resident_name,

                "first_name":
                    row[3],

                "middle_name":
                    row[4],

                "last_name":
                    row[5],

                "suffix":
                    row[6],

                "address":
                    row[7],

                "email":
                    row[8],

                "contact_number":
                    row[9],

                "document_type_id":
                    row[10],

                "document_name":
                    row[11],

                "purpose":
                    row[12],

                "institution":
                    row[13],

                "request_notes":
                    row[14],

                "delivery_method":
                    row[15],

                "payment_method":
                    row[16],

                "status":
                    row[17],

                "created_at":
                    row[18],

                "updated_at":
                    row[19],
            })

    except Exception as e:

        print(
            "DOCUMENT REQUEST LIST ERROR:",
            e
        )

        messages.error(
            request,
            "Unable to load document requests."
        )

    # =====================================================
    # STATISTICS
    # =====================================================

    total_requests = 0
    pending_requests = 0
    ready_requests = 0
    released_requests = 0

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT

                    COUNT(*),

                    SUM(
                        CASE
                            WHEN status IN (
                                'Submitted',
                                'Under Verification',
                                'Ready for Signature'
                            )
                            THEN 1
                            ELSE 0
                        END
                    ),

                    SUM(
                        CASE
                            WHEN status =
                                'Ready for Pickup'
                            THEN 1
                            ELSE 0
                        END
                    ),

                    SUM(
                        CASE
                            WHEN status =
                                'Released'
                            THEN 1
                            ELSE 0
                        END
                    )

                FROM document_requests
                """
            )

            stats = cursor.fetchone()

        if stats:

            total_requests = stats[0] or 0
            pending_requests = stats[1] or 0
            ready_requests = stats[2] or 0
            released_requests = stats[3] or 0

    except Exception as e:

        print(
            "DOCUMENT REQUEST "
            "STATISTICS ERROR:",
            e
        )

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        "document_requests":
            document_requests,

        "document_types":
            document_types,

        "statuses":
            DOCUMENT_REQUEST_STATUSES,

        "total_requests":
            total_requests,

        "pending_requests":
            pending_requests,

        "ready_requests":
            ready_requests,

        "released_requests":
            released_requests,

        "search":
            search,

        "selected_status":
            status_filter,

        "selected_document_type":
            document_filter,
    }

    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "docrequestmodule/request_documents.html",
        context
    )


# =========================================================
# UPDATE DOCUMENT REQUEST STATUS
# =========================================================

@role_required("admin", "official")
@require_POST
def update_request_status(
    request,
    request_id
):

    new_status = (
        request.POST.get(
            "status",
            ""
        )
        .strip()
    )

    # =====================================================
    # VALIDATE STATUS
    # =====================================================

    if new_status not in DOCUMENT_REQUEST_STATUSES:

        messages.error(
            request,
            "Invalid document request status."
        )

        return redirect(
            "docrequestmodule:request_documents"
        )

    # =====================================================
    # UPDATE DATABASE
    # =====================================================

    try:

        with transaction.atomic():

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE document_requests

                    SET
                        status = %s,
                        updated_at = NOW()

                    WHERE
                        request_id = %s
                    """,
                    [
                        new_status,
                        request_id,
                    ]
                )

                if cursor.rowcount == 0:

                    messages.error(
                        request,
                        "Document request was not found."
                    )

                    return redirect(
                        "docrequestmodule:request_documents"
                    )

        messages.success(
            request,
            (
                "Document request status "
                f"updated to {new_status}."
            )
        )

    except Exception as e:

        print(
            "DOCUMENT REQUEST "
            "STATUS UPDATE ERROR:",
            e
        )

        messages.error(
            request,
            (
                "Unable to update the "
                "document request status."
            )
        )

    return redirect(
        "docrequestmodule:request_documents"
    )