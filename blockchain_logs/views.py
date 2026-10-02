from django.shortcuts import render
from django.core.paginator import Paginator

from .models import BlockchainLog


def blockchain_logs(request):

    # =========================================================
    # GET FILTER VALUES
    # =========================================================

    search = request.GET.get(
        "search",
        ""
    ).strip()

    document_type = request.GET.get(
        "document_type",
        ""
    ).strip()

    action = request.GET.get(
        "action",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        ""
    ).strip()

    verification_status = request.GET.get(
        "verification_status",
        ""
    ).strip()


    # =========================================================
    # GET BLOCKCHAIN LOGS
    # =========================================================

    logs = BlockchainLog.objects.all().order_by(
        "-recorded_at",
        "-blockchain_log_id"
    )


    # =========================================================
    # SEARCH
    # =========================================================

    if search:

        logs = logs.filter(
            blockchain_document_id__icontains=search
        )


    # =========================================================
    # DOCUMENT TYPE FILTER
    # =========================================================

    if document_type:

        logs = logs.filter(
            document_type=document_type
        )


    # =========================================================
    # ACTION FILTER
    # =========================================================

    if action:

        logs = logs.filter(
            action=action
        )


    # =========================================================
    # STATUS FILTER
    # =========================================================

    if status:

        logs = logs.filter(
            status=status
        )


    # =========================================================
    # VERIFICATION STATUS FILTER
    # =========================================================

    if verification_status:

        logs = logs.filter(
            verification_status=verification_status
        )


    # =========================================================
    # PAGINATION
    # 10 BLOCKCHAIN LOGS PER PAGE
    # =========================================================

    paginator = Paginator(
        logs,
        10
    )

    page_number = request.GET.get(
        "page"
    )

    logs = paginator.get_page(
        page_number
    )


    # =========================================================
    # STATISTICS
    # =========================================================

    total_logs = BlockchainLog.objects.count()

    successful_logs = BlockchainLog.objects.filter(
        status="SUCCESS"
    ).count()

    failed_logs = BlockchainLog.objects.filter(
        status="FAILED"
    ).count()

    confirmed_logs = BlockchainLog.objects.filter(
        verification_status="Confirmed"
    ).count()


    # =========================================================
    # CONTEXT
    # =========================================================

    context = {

        "logs": logs,

        "total_logs": total_logs,

        "successful_logs": successful_logs,

        "failed_logs": failed_logs,

        "confirmed_logs": confirmed_logs,

        "search": search,

        "selected_document_type":
            document_type,

        "selected_action":
            action,

        "selected_status":
            status,

        "selected_verification_status":
            verification_status,
    }


    # =========================================================
    # RENDER
    # =========================================================

    return render(
        request,
        "blockchain_logs/blockchain_logs.html",
        context
    )