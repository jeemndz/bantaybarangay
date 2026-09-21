from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password

from .models import User


# =====================================================
# LOGIN
# =====================================================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        remember = request.POST.get("remember")

        # -------------------------------------------------
        # EMPTY FIELDS
        # -------------------------------------------------

        if not username or not password:

            messages.error(
                request,
                "Please enter your username and password."
            )

            return render(
                request,
                "login/login.html"
            )

        # -------------------------------------------------
        # FIND USER
        # -------------------------------------------------

        try:

            user = User.objects.get(
                username=username
            )

        except User.DoesNotExist:

            messages.error(
                request,
                "Invalid username or password."
            )

            return render(
                request,
                "login/login.html"
            )

        # -------------------------------------------------
        # CHECK ACCOUNT STATUS
        # -------------------------------------------------

        if not user.is_active:

            messages.error(
                request,
                "Your account is currently inactive."
            )

            return render(
                request,
                "login/login.html"
            )

        # -------------------------------------------------
        # CHECK PASSWORD
        # -------------------------------------------------

        password_valid = False

        try:

            password_valid = check_password(
                password,
                user.password_hash
            )

        except Exception:

            password_valid = False

        # -------------------------------------------------
        # SUPPORT PLAIN TEXT PASSWORD
        # -------------------------------------------------

        if not password_valid:

            password_valid = (
                password == user.password_hash
            )

        # -------------------------------------------------
        # INVALID PASSWORD
        # -------------------------------------------------

        if not password_valid:

            messages.error(
                request,
                "Invalid username or password."
            )

            return render(
                request,
                "login/login.html"
            )

        # =================================================
        # LOGIN SUCCESSFUL
        # =================================================

        # Clear any previous session
        request.session.flush()

        # -------------------------------------------------
        # GET USER INFORMATION
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

        email = getattr(
            user,
            "email",
            ""
        ) or ""

        role = getattr(
            user,
            "role",
            ""
        ) or ""

        # Full name
        full_name = f"{first_name} {last_name}".strip()

        if not full_name:
            full_name = user.username

        # -------------------------------------------------
        # GENERATE INITIALS
        # -------------------------------------------------

        if first_name and last_name:

            initials = (
                first_name[0] +
                last_name[0]
            ).upper()

        elif first_name:

            initials = first_name[:2].upper()

        else:

            initials = user.username[:2].upper()

        # -------------------------------------------------
        # STORE USER SESSION
        # -------------------------------------------------

        request.session["is_logged_in"] = True

        request.session["user_id"] = user.user_id

        request.session["username"] = user.username

        request.session["first_name"] = first_name

        request.session["last_name"] = last_name

        request.session["full_name"] = full_name

        request.session["email"] = email

        request.session["role"] = role

        request.session["initials"] = initials

        # -------------------------------------------------
        # REMEMBER ME
        # -------------------------------------------------

        if remember:

            # 14 days
            request.session.set_expiry(
                60 * 60 * 24 * 14
            )

        else:

            # Session expires when browser closes
            request.session.set_expiry(0)

        # -------------------------------------------------
        # ROLE REDIRECTION
        # -------------------------------------------------

        normalized_role = role.strip().lower()

        if normalized_role in [
            "admin",
            "official"
        ]:

            return redirect("dashboard")

        elif normalized_role == "resident":

            return redirect("home")

        else:

            messages.error(
                request,
                f"Invalid account role: {role}"
            )

            request.session.flush()

            return render(
                request,
                "login/login.html"
            )

    # =====================================================
    # GET REQUEST
    # =====================================================

    return render(
        request,
        "login/login.html"
    )


# =====================================================
# LOGOUT
# =====================================================

def logout_view(request):

    # Completely remove the logged-in session
    request.session.flush()

    messages.success(
        request,
        "You have been successfully signed out."
    )

    return redirect("login")