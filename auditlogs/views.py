from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from .models import AuditLog
from bantaybarangay.security import role_required

try:
    from login.models import User
except ImportError:
    User = None


# =========================================================
# AUDIT LOGS
# =========================================================
@role_required("admin")
def audit_logs(request):
    """
    Display the Audit Logs page with:
    - statistics
    - search
    - module filtering
    - action filtering
    - date filtering
    - pagination
    - user display names
    """

    # =====================================================
    # BASE QUERY
    # =====================================================

    base_queryset = AuditLog.objects.all().order_by(
        "-created_at",
        "-audit_id"
    )


    # =====================================================
    # STATISTICS
    # =====================================================

    total_logs = base_queryset.count()

    today = timezone.localdate()

    today_logs = base_queryset.filter(
        created_at__date=today
    ).count()

    active_users = (
        base_queryset
        .exclude(user_id__isnull=True)
        .values("user_id")
        .distinct()
        .count()
    )

    module_count = (
        base_queryset
        .exclude(module__isnull=True)
        .exclude(module="")
        .values("module")
        .distinct()
        .count()
    )


    # =====================================================
    # AVAILABLE MODULES
    # =====================================================

    modules = list(
        base_queryset
        .exclude(module__isnull=True)
        .exclude(module="")
        .values_list(
            "module",
            flat=True
        )
        .distinct()
        .order_by("module")
    )


    # =====================================================
    # AVAILABLE ACTIONS
    # =====================================================

    actions = list(
        base_queryset
        .exclude(action__isnull=True)
        .exclude(action="")
        .values_list(
            "action",
            flat=True
        )
        .distinct()
        .order_by("action")
    )


    # =====================================================
    # GET FILTER VALUES
    # =====================================================

    search_query = request.GET.get(
        "search",
        ""
    ).strip()

    selected_module = request.GET.get(
        "module",
        ""
    ).strip()

    selected_action = request.GET.get(
        "action",
        ""
    ).strip()

    selected_date = request.GET.get(
        "date",
        ""
    ).strip()


    # =====================================================
    # FILTERED QUERYSET
    # =====================================================

    logs_queryset = base_queryset


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    if search_query:

        search_filter = (
            Q(action__icontains=search_query)
            |
            Q(module__icontains=search_query)
            |
            Q(description__icontains=search_query)
            |
            Q(ip_address__icontains=search_query)
        )

        # Allow searching numeric user IDs.
        if search_query.isdigit():

            search_filter |= Q(
                user_id=int(search_query)
            )

        logs_queryset = logs_queryset.filter(
            search_filter
        )


    # -----------------------------------------------------
    # MODULE
    # -----------------------------------------------------

    if selected_module:

        logs_queryset = logs_queryset.filter(
            module=selected_module
        )


    # -----------------------------------------------------
    # ACTION
    # -----------------------------------------------------

    if selected_action:

        logs_queryset = logs_queryset.filter(
            action=selected_action
        )


    # -----------------------------------------------------
    # DATE
    # -----------------------------------------------------

    if selected_date:

        try:

            filter_date = datetime.strptime(
                selected_date,
                "%Y-%m-%d"
            ).date()

            logs_queryset = logs_queryset.filter(
                created_at__date=filter_date
            )

        except ValueError:

            # Ignore malformed date parameters.
            selected_date = ""


    # =====================================================
    # FILTERED RESULT COUNT
    # =====================================================

    filtered_count = logs_queryset.count()


    # =====================================================
    # PAGINATION
    # =====================================================

    paginator = Paginator(
        logs_queryset,
        10
    )

    page_number = request.GET.get(
        "page",
        1
    )

    page_obj = paginator.get_page(
        page_number
    )


    # =====================================================
    # PREPARE CURRENT PAGE
    # =====================================================

    audit_log_list = list(
        page_obj.object_list
    )


    # =====================================================
    # GET USER IDS
    # =====================================================

    user_ids = {
        log.user_id
        for log in audit_log_list
        if log.user_id
    }


    # =====================================================
    # LOAD USERS
    # =====================================================

    users_by_id = {}

    if User is not None and user_ids:

        try:

            users = User.objects.filter(
                user_id__in=user_ids
            )

            users_by_id = {
                user.user_id: user
                for user in users
            }

        except Exception:

            users_by_id = {}


    # =====================================================
    # USER DISPLAY NAME
    # =====================================================

    for log in audit_log_list:

        if not log.user_id:

            log.user = "System"
            continue


        user = users_by_id.get(
            log.user_id
        )


        if not user:

            log.user = (
                f"User #{log.user_id}"
            )

            continue


        # -------------------------------------------------
        # TRY FULL NAME
        # -------------------------------------------------

        first_name = getattr(
            user,
            "first_name",
            ""
        ) or ""

        last_name = getattr(
            user,
            "last_name",
            ""
        ) or ""

        full_name = (
            f"{first_name} {last_name}"
        ).strip()


        # -------------------------------------------------
        # FALLBACK TO USERNAME
        # -------------------------------------------------

        username = getattr(
            user,
            "username",
            ""
        ) or ""


        if full_name:

            log.user = full_name

        elif username:

            log.user = username

        else:

            log.user = (
                f"User #{log.user_id}"
            )


    # =====================================================
    # REPLACE PAGE OBJECT LIST
    # =====================================================

    page_obj.object_list = audit_log_list


    # =====================================================
    # QUERY STRING FOR PAGINATION
    # =====================================================

    query_params = request.GET.copy()

    if "page" in query_params:
        query_params.pop("page")

    filter_query_string = (
        query_params.urlencode()
    )


    # =====================================================
    # FILTER STATUS
    # =====================================================

    filters_active = bool(
        search_query
        or selected_module
        or selected_action
        or selected_date
    )


    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        # ---------------------------------------------
        # LOG DATA
        # ---------------------------------------------

        "audit_logs":
            audit_log_list,

        "page_obj":
            page_obj,

        "filtered_count":
            filtered_count,


        # ---------------------------------------------
        # STATISTICS
        # ---------------------------------------------

        "total_logs":
            total_logs,

        "today_logs":
            today_logs,

        "active_users":
            active_users,

        "module_count":
            module_count,


        # ---------------------------------------------
        # FILTER OPTIONS
        # ---------------------------------------------

        "modules":
            modules,

        "actions":
            actions,


        # ---------------------------------------------
        # CURRENT FILTERS
        # ---------------------------------------------

        "search_query":
            search_query,

        "selected_module":
            selected_module,

        "selected_action":
            selected_action,

        "selected_date":
            selected_date,

        "filters_active":
            filters_active,


        # ---------------------------------------------
        # PAGINATION
        # ---------------------------------------------

        "filter_query_string":
            filter_query_string,

    }


    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "auditlogs/audit_logs.html",
        context
    )