from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import User


# =========================================================
# MANAGED USER ROLES
# =========================================================
# Residents are intentionally NOT managed in this module.
# Resident accounts belong to the resident management flow.

MANAGED_ROLES = {
    "official",
    "admin",
}


# =========================================================
# USER MANAGEMENT
# =========================================================

def user_list(request):

    # =====================================================
    # POST REQUESTS
    # =====================================================

    if request.method == "POST":

        action = request.POST.get(
            "action",
            ""
        ).strip()

        # =================================================
        # CREATE USER
        # =================================================

        if action == "create_user":

            username = request.POST.get(
                "username",
                ""
            ).strip()

            email = request.POST.get(
                "email",
                ""
            ).strip()

            role = request.POST.get(
                "role",
                ""
            ).strip().lower()

            password = request.POST.get(
                "password",
                ""
            )

            is_active = (
                request.POST.get(
                    "is_active",
                    "1"
                ) == "1"
            )

            # ---------------------------------------------
            # REQUIRED FIELDS
            # ---------------------------------------------

            if not username:

                messages.error(
                    request,
                    "Username is required."
                )

                return redirect(
                    "usermanagement:user_list"
                )

            if not email:

                messages.error(
                    request,
                    "Email is required."
                )

                return redirect(
                    "usermanagement:user_list"
                )

            if not password:

                messages.error(
                    request,
                    "Password is required."
                )

                return redirect(
                    "usermanagement:user_list"
                )

            # ---------------------------------------------
            # PASSWORD VALIDATION
            # ---------------------------------------------

            if len(password) < 8:

                messages.error(
                    request,
                    "Password must contain at least 8 characters."
                )

                return redirect(
                    "usermanagement:user_list"
                )

            # ---------------------------------------------
            # ROLE VALIDATION
            # ---------------------------------------------

            if role not in MANAGED_ROLES:

                messages.error(
                    request,
                    "Invalid user role."
                )

                return redirect(
                    "usermanagement:user_list"
                )

            # ---------------------------------------------
            # DUPLICATE USERNAME
            # ---------------------------------------------

            if User.objects.filter(
                username__iexact=username
            ).exists():

                messages.error(
                    request,
                    "That username is already being used."
                )

                return redirect(
                    "usermanagement:user_list"
                )

            # ---------------------------------------------
            # DUPLICATE EMAIL
            # ---------------------------------------------

            if User.objects.filter(
                email__iexact=email
            ).exists():

                messages.error(
                    request,
                    "That email address is already being used."
                )

                return redirect(
                    "usermanagement:user_list"
                )

            # ---------------------------------------------
            # CREATE USER
            # ---------------------------------------------

            User.objects.create(
                username=username,
                password_hash=make_password(password),
                email=email,
                role=role,
                is_active=is_active,
            )

            messages.success(
                request,
                f'User "{username}" was created successfully.'
            )

            return redirect(
                "usermanagement:user_list"
            )

        # =================================================
        # EDIT USER
        # =================================================

        elif action == "edit_user":

            user_id = request.POST.get(
                "user_id"
            )

            username = request.POST.get(
                "username",
                ""
            ).strip()

            email = request.POST.get(
                "email",
                ""
            ).strip()

            role = request.POST.get(
                "role",
                ""
            ).strip().lower()

            is_active = (
                request.POST.get(
                    "is_active",
                    "1"
                ) == "1"
            )

            # ---------------------------------------------
            # GET USER
            # ---------------------------------------------

            user = get_object_or_404(
                User,
                user_id=user_id
            )

            # Do not allow resident accounts to be edited
            # through User Management.

            if user.role == "resident":

                messages.error(
                    request,
                    "Resident accounts cannot be managed here."
                )

                return redirect(
                    "usermanagement:user_list"
                )

            # ---------------------------------------------
            # VALIDATION
            # ---------------------------------------------

            if not username:

                messages.error(
                    request,
                    "Username is required."
                )

                return redirect(
                    "usermanagement:user_list"
                )

            if not email:

                messages.error(
                    request,
                    "Email is required."
                )

                return redirect(
                    "usermanagement:user_list"
                )

            if role not in MANAGED_ROLES:

                messages.error(
                    request,
                    "Invalid user role."
                )

                return redirect(
                    "usermanagement:user_list"
                )

            # ---------------------------------------------
            # DUPLICATE USERNAME
            # ---------------------------------------------

            username_exists = (
                User.objects
                .filter(
                    username__iexact=username
                )
                .exclude(
                    user_id=user.user_id
                )
                .exists()
            )

            if username_exists:

                messages.error(
                    request,
                    "That username is already being used."
                )

                return redirect(
                    "usermanagement:user_list"
                )

            # ---------------------------------------------
            # DUPLICATE EMAIL
            # ---------------------------------------------

            email_exists = (
                User.objects
                .filter(
                    email__iexact=email
                )
                .exclude(
                    user_id=user.user_id
                )
                .exists()
            )

            if email_exists:

                messages.error(
                    request,
                    "That email address is already being used."
                )

                return redirect(
                    "usermanagement:user_list"
                )

            # ---------------------------------------------
            # UPDATE USER
            # ---------------------------------------------

            user.username = username
            user.email = email
            user.role = role
            user.is_active = is_active

            user.save()

            messages.success(
                request,
                f'User "{username}" was updated successfully.'
            )

            return redirect(
                "usermanagement:user_list"
            )

        # =================================================
        # RESET PASSWORD
        # =================================================

        elif action == "reset_password":

            user_id = request.POST.get(
                "user_id"
            )

            password = request.POST.get(
                "password",
                ""
            )

            user = get_object_or_404(
                User,
                user_id=user_id
            )

            # ---------------------------------------------
            # PREVENT RESIDENT MANAGEMENT
            # ---------------------------------------------

            if user.role == "resident":

                messages.error(
                    request,
                    "Resident accounts cannot be managed here."
                )

                return redirect(
                    "usermanagement:user_list"
                )

            # ---------------------------------------------
            # PASSWORD VALIDATION
            # ---------------------------------------------

            if not password:

                messages.error(
                    request,
                    "New password is required."
                )

                return redirect(
                    "usermanagement:user_list"
                )

            if len(password) < 8:

                messages.error(
                    request,
                    "Password must contain at least 8 characters."
                )

                return redirect(
                    "usermanagement:user_list"
                )

            # ---------------------------------------------
            # UPDATE PASSWORD
            # ---------------------------------------------

            user.password_hash = make_password(
                password
            )

            user.save()

            messages.success(
                request,
                f'Password for "{user.username}" was reset successfully.'
            )

            return redirect(
                "usermanagement:user_list"
            )

        # =================================================
        # DISABLE USER
        # =================================================

        elif action == "disable_user":

            user_id = request.POST.get(
                "user_id"
            )

            user = get_object_or_404(
                User,
                user_id=user_id
            )

            if user.role == "resident":

                messages.error(
                    request,
                    "Resident accounts cannot be managed here."
                )

                return redirect(
                    "usermanagement:user_list"
                )

            user.is_active = False

            user.save()

            messages.success(
                request,
                f'User "{user.username}" was disabled.'
            )

            return redirect(
                "usermanagement:user_list"
            )

        # =================================================
        # ENABLE USER
        # =================================================

        elif action == "enable_user":

            user_id = request.POST.get(
                "user_id"
            )

            user = get_object_or_404(
                User,
                user_id=user_id
            )

            if user.role == "resident":

                messages.error(
                    request,
                    "Resident accounts cannot be managed here."
                )

                return redirect(
                    "usermanagement:user_list"
                )

            user.is_active = True

            user.save()

            messages.success(
                request,
                f'User "{user.username}" was enabled.'
            )

            return redirect(
                "usermanagement:user_list"
            )

        # =================================================
        # INVALID ACTION
        # =================================================

        else:

            messages.error(
                request,
                "Invalid user management action."
            )

            return redirect(
                "usermanagement:user_list"
            )

    # =====================================================
    # GET REQUEST
    # =====================================================

    # IMPORTANT:
    # Residents are excluded from this module.

    managed_users = (
        User.objects
        .exclude(role="resident")
    )

    users_queryset = (
        managed_users
        .order_by("-created_at")
    )

    # =====================================================
    # SEARCH
    # =====================================================

    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    if search_query:

        users_queryset = (
            users_queryset.filter(

                Q(
                    username__icontains=search_query
                )

                |

                Q(
                    email__icontains=search_query
                )

                |

                Q(
                    role__icontains=search_query
                )
            )
        )

    # =====================================================
    # ROLE FILTER
    # =====================================================

    role_filter = request.GET.get(
        "role",
        ""
    ).strip().lower()

    if role_filter in MANAGED_ROLES:

        users_queryset = (
            users_queryset.filter(
                role=role_filter
            )
        )

    # =====================================================
    # STATUS FILTER
    # =====================================================

    status_filter = request.GET.get(
        "status",
        ""
    ).strip().lower()

    if status_filter == "active":

        users_queryset = (
            users_queryset.filter(
                is_active=True
            )
        )

    elif status_filter == "disabled":

        users_queryset = (
            users_queryset.filter(
                is_active=False
            )
        )

    # =====================================================
    # STATISTICS
    # =====================================================

    total_users = (
        managed_users.count()
    )

    active_users = (
        managed_users
        .filter(
            is_active=True
        )
        .count()
    )

    disabled_users = (
        managed_users
        .filter(
            is_active=False
        )
        .count()
    )

    administrator_count = (
        managed_users
        .filter(
            role="admin"
        )
        .count()
    )

    official_count = (
        managed_users
        .filter(
            role="official"
        )
        .count()
    )

    # =====================================================
    # PAGINATION
    # =====================================================

    paginator = Paginator(
        users_queryset,
        10
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        "users":
            page_obj,

        "page_obj":
            page_obj,

        "total_users":
            total_users,

        "active_users":
            active_users,

        "disabled_users":
            disabled_users,

        "administrator_count":
            administrator_count,

        "official_count":
            official_count,

        # Keep these aliases so the current HTML
        # statistics cards also work.

        "administrators":
            administrator_count,

        "barangay_officials":
            official_count,

        "search_query":
            search_query,

        "role_filter":
            role_filter,

        "status_filter":
            status_filter,
    }

    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "usermanagement/user_list.html",
        context
    )