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

        # -------------------------------------------------
        # STORE USER SESSION
        # -------------------------------------------------

        request.session["user_id"] = user.user_id
        request.session["username"] = user.username
        request.session["email"] = user.email
        request.session["role"] = user.role

        # -------------------------------------------------
        # REMEMBER ME
        # -------------------------------------------------

        if remember:

            request.session.set_expiry(
                60 * 60 * 24 * 14
            )

        else:

            request.session.set_expiry(0)

        # -------------------------------------------------
        # ROLE REDIRECTION
        # -------------------------------------------------

        role = user.role.strip().lower()

        if role in ["admin", "official"]:

            return redirect("dashboard")

        elif role == "resident":

            return redirect("home")

        else:

            messages.error(
                request,
                f"Invalid account role: {user.role}"
            )

            request.session.flush()

            return render(
                request,
                "login/login.html"
            )

    # -------------------------------------------------
    # GET REQUEST
    # -------------------------------------------------

    return render(
        request,
        "login/login.html"
    )


# =====================================================
# LOGOUT
# =====================================================

def logout_view(request):

    request.session.flush()

    return redirect("login")