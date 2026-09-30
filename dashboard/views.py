from datetime import date

from django.db import connection
from django.shortcuts import render, redirect


# =========================================================
# DATABASE HELPERS
# =========================================================

def fetch_one(query, params=None):
    """
    Execute a query and return the first column
    from the first row.
    """

    with connection.cursor() as cursor:

        cursor.execute(
            query,
            params or []
        )

        row = cursor.fetchone()

    if not row:
        return 0

    return row[0] or 0


def fetch_all_dict(query, params=None):
    """
    Execute a query and return rows as dictionaries.
    """

    with connection.cursor() as cursor:

        cursor.execute(
            query,
            params or []
        )

        columns = [
            column[0]
            for column in cursor.description
        ]

        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


# =========================================================
# DASHBOARD
# =========================================================

def dashboard(request):

    # =====================================================
    # LOGIN CHECK
    # =====================================================

    if not request.session.get("is_logged_in"):

        return redirect("login")


    # =====================================================
    # ROLE CHECK
    # =====================================================

    role = (
        request.session.get(
            "role",
            ""
        )
        or ""
    ).strip().lower()

    if role not in [
        "admin",
        "official"
    ]:

        return redirect("home")


    # =====================================================
    # CURRENT DATE
    # =====================================================

    today = date.today()

    current_year = today.year

    previous_year = current_year - 1


    # =====================================================
    # TOTAL COMPLAINTS
    # =====================================================

    total_complaints = fetch_one(
        """
        SELECT COUNT(*)
        FROM complaints
        """
    )


    # =====================================================
    # ACTIVE CASES
    # =====================================================

    terminal_statuses = [
        "Settled",
        "Resolved",
        "Rejected",
        "Closed",
    ]

    active_cases = fetch_one(
        """
        SELECT COUNT(*)
        FROM complaints
        WHERE status NOT IN (%s, %s, %s, %s)
        """,
        terminal_statuses
    )


    # =====================================================
    # COMMUNITY / INCIDENT REPORTS
    # =====================================================

    incident_reports = fetch_one(
        """
        SELECT COUNT(*)
        FROM complaints
        WHERE report_type = %s
        """,
        [
            "Community Issue"
        ]
    )


    # =====================================================
    # RELEASED DOCUMENTS
    # =====================================================

    released_documents = fetch_one(
        """
        SELECT COUNT(*)
        FROM document_requests
        WHERE status = %s
        """,
        [
            "Released"
        ]
    )


    # =====================================================
    # VERIFIED RESIDENTS
    # =====================================================

    total_residents = fetch_one(
        """
        SELECT COUNT(*)
        FROM residents
        WHERE verification_status = %s
        """,
        [
            "Verified"
        ]
    )


    # =====================================================
    # PENDING / SCHEDULED HEARINGS
    # =====================================================

    pending_hearings = fetch_one(
        """
        SELECT COUNT(*)
        FROM hearings
        WHERE status = %s
        """,
        [
            "Scheduled"
        ]
    )


    # =====================================================
    # PENDING RESIDENT REGISTRATIONS
    # =====================================================

    pending_residents = fetch_one(
        """
        SELECT COUNT(*)
        FROM residents
        WHERE verification_status = %s
        """,
        [
            "Pending"
        ]
    )


    # =====================================================
    # DOCUMENTS UNDER VERIFICATION
    # =====================================================

    pending_documents = fetch_one(
        """
        SELECT COUNT(*)
        FROM document_requests
        WHERE status = %s
        """,
        [
            "Under Verification"
        ]
    )


    # =====================================================
    # UPCOMING HEARINGS
    # =====================================================

    upcoming_hearings_count = fetch_one(
        """
        SELECT COUNT(*)
        FROM hearings
        WHERE status = %s
          AND hearing_date >= %s
        """,
        [
            "Scheduled",
            today,
        ]
    )


    # =====================================================
    # NEXT HEARING
    # =====================================================

    next_hearing_rows = fetch_all_dict(
        """
        SELECT
            hearing_id,
            case_number,
            complainant_name,
            respondent_name,
            hearing_date,
            start_time,
            chamber
        FROM hearings
        WHERE status = %s
          AND hearing_date >= %s
        ORDER BY
            hearing_date ASC,
            start_time ASC
        LIMIT 1
        """,
        [
            "Scheduled",
            today,
        ]
    )

    next_hearing = (
        next_hearing_rows[0]
        if next_hearing_rows
        else None
    )


    # =====================================================
    # RECENT COMPLAINTS
    # =====================================================

    recent_complaints = fetch_all_dict(
        """
        SELECT
            c.complaint_id,
            c.resident_id,
            c.complaint_type,
            c.subject,
            c.status,
            c.priority,
            c.submitted_at,

            r.first_name,
            r.middle_name,
            r.last_name,
            r.suffix

        FROM complaints c

        LEFT JOIN residents r
            ON r.resident_id = c.resident_id

        ORDER BY
            c.submitted_at DESC,
            c.complaint_id DESC

        LIMIT 5
        """
    )


    # =====================================================
    # PREPARE COMPLAINANT NAMES / STATUS CLASSES
    # =====================================================

    for complaint in recent_complaints:

        name_parts = [
            complaint.get("first_name"),
            complaint.get("middle_name"),
            complaint.get("last_name"),
            complaint.get("suffix"),
        ]

        complaint["complainant_name"] = " ".join(
            str(part).strip()
            for part in name_parts
            if part
        )

        if not complaint["complainant_name"]:

            complaint["complainant_name"] = (
                f"Resident #{complaint['resident_id']}"
            )


        status = (
            complaint.get("status")
            or ""
        ).lower()


        if status in [
            "resolved",
            "settled",
            "closed",
        ]:

            complaint["status_class"] = "resolved"

        elif status == "rejected":

            complaint["status_class"] = "rejected"

        elif status in [
            "hearing scheduled",
            "under mediation",
            "summons issued",
        ]:

            complaint["status_class"] = "approved"

        else:

            complaint["status_class"] = "pending"


    # =====================================================
    # MONTHLY COMPLAINT TREND
    # =====================================================

    monthly_rows = fetch_all_dict(
        """
        SELECT
            MONTH(submitted_at) AS month_number,
            COUNT(*) AS total

        FROM complaints

        WHERE YEAR(submitted_at) = %s

        GROUP BY MONTH(submitted_at)

        ORDER BY MONTH(submitted_at)
        """,
        [
            current_year
        ]
    )


    # =====================================================
    # PREVIOUS YEAR TREND
    # =====================================================

    previous_monthly_rows = fetch_all_dict(
        """
        SELECT
            MONTH(submitted_at) AS month_number,
            COUNT(*) AS total

        FROM complaints

        WHERE YEAR(submitted_at) = %s

        GROUP BY MONTH(submitted_at)

        ORDER BY MONTH(submitted_at)
        """,
        [
            previous_year
        ]
    )


    current_month_counts = {
        row["month_number"]: row["total"]
        for row in monthly_rows
    }

    previous_month_counts = {
        row["month_number"]: row["total"]
        for row in previous_monthly_rows
    }


    month_names = [
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC",
    ]


    max_month_value = max(
        [
            *current_month_counts.values(),
            *previous_month_counts.values(),
            1,
        ]
    )


    monthly_complaints = []

    for month_number in range(1, 13):

        current_total = current_month_counts.get(
            month_number,
            0
        )

        previous_total = previous_month_counts.get(
            month_number,
            0
        )

        current_height = (
            current_total /
            max_month_value
        ) * 100

        previous_height = (
            previous_total /
            max_month_value
        ) * 100


        monthly_complaints.append(
            {
                "month": month_names[
                    month_number - 1
                ],

                "current_total":
                    current_total,

                "previous_total":
                    previous_total,

                "current_height":
                    round(
                        current_height,
                        2
                    ),

                "previous_height":
                    round(
                        previous_height,
                        2
                    ),
            }
        )


    # =====================================================
    # COMPLAINT CATEGORIES
    # =====================================================

    category_rows = fetch_all_dict(
        """
        SELECT
            complaint_type,
            COUNT(*) AS total

        FROM complaints

        GROUP BY complaint_type

        ORDER BY total DESC
        """
    )


    category_total = sum(
        row["total"]
        for row in category_rows
    )


    incident_categories = []

    for index, row in enumerate(
        category_rows[:4]
    ):

        percentage = 0

        if category_total:

            percentage = round(
                (
                    row["total"] /
                    category_total
                ) * 100
            )


        incident_categories.append(
            {
                "name":
                    row["complaint_type"],

                "total":
                    row["total"],

                "percentage":
                    percentage,

                "dot_class":
                    [
                        "one",
                        "two",
                        "three",
                        "four",
                    ][index],
            }
        )


    # =====================================================
    # RECENT SYSTEM ACTIVITY
    # =====================================================

    recent_activity = fetch_all_dict(
        """
        SELECT
            audit_id,
            user_id,
            action,
            module,
            description,
            ip_address,
            created_at

        FROM audit_logs

        ORDER BY
            created_at DESC,
            audit_id DESC

        LIMIT 5
        """
    )


    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        # Summary cards
        "total_complaints":
            total_complaints,

        "active_cases":
            active_cases,

        "incident_reports":
            incident_reports,

        "released_documents":
            released_documents,

        "total_residents":
            total_residents,

        "pending_hearings":
            pending_hearings,


        # Chart
        "current_year":
            current_year,

        "previous_year":
            previous_year,

        "monthly_complaints":
            monthly_complaints,


        # Categories
        "incident_categories":
            incident_categories,

        "category_total":
            category_total,


        # Recent information
        "recent_complaints":
            recent_complaints,

        "recent_activity":
            recent_activity,


        # Alerts
        "pending_residents":
            pending_residents,

        "pending_documents":
            pending_documents,

        "upcoming_hearings_count":
            upcoming_hearings_count,

        "next_hearing":
            next_hearing,
    }


    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )