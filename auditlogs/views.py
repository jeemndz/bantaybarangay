from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils import timezone

from .models import AuditLog


# =========================================================
# AUDIT LOGS
# =========================================================

def audit_logs(request):
    """
    Display the Audit Logs page.
    """

    # =====================================================
    # BASE QUERY
    # =====================================================

    logs_queryset = AuditLog.objects.all().order_by(
        "-created_at",
        "-audit_id"
    )


    # =====================================================
    # STATISTICS
    # =====================================================

    total_logs = logs_queryset.count()


    # =====================================================
    # TODAY'S LOGS
    # =====================================================

    today = timezone.localdate()

    today_logs = logs_queryset.filter(
        created_at__date=today
    ).count()


    # =====================================================
    # ACTIVE USERS
    # =====================================================

    active_users = (
        logs_queryset
        .exclude(user_id__isnull=True)
        .values("user_id")
        .distinct()
        .count()
    )


    # =====================================================
    # MODULE COUNT
    # =====================================================

    module_count = (
        logs_queryset
        .exclude(module__isnull=True)
        .exclude(module="")
        .values("module")
        .distinct()
        .count()
    )


    # =====================================================
    # MODULE LIST
    # =====================================================

    modules = list(
        logs_queryset
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
    # PREPARE LOG DATA
    # =====================================================

    audit_log_list = list(
        page_obj.object_list
    )


    # =====================================================
    # USER DISPLAY
    # =====================================================

    for log in audit_log_list:

        if log.user_id:

            log.user = (
                f"User #{log.user_id}"
            )

        else:

            log.user = "System"


    page_obj.object_list = audit_log_list


    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        "audit_logs":
            audit_log_list,

        "page_obj":
            page_obj,

        "total_logs":
            total_logs,

        "today_logs":
            today_logs,

        "active_users":
            active_users,

        "module_count":
            module_count,

        "modules":
            modules,

    }


    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "auditlogs/audit_logs.html",
        context
    )