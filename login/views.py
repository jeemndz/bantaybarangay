from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

import secrets

from .models import User


# =====================================================
# LOGIN
# =====================================================

def login_view(request):

    # =================================================
    # ALREADY LOGGED IN
    # =================================================

    if request.session.get("is_logged_in"):

        role = (
            request.session.get("role", "")
            or ""
        ).strip().lower()

        if role in [
            "admin",
            "official"
        ]:

            return redirect("dashboard")

        elif role == "resident":

            return redirect("home")


    # =================================================
    # POST REQUEST
    # =================================================

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        remember = request.POST.get(
            "remember"
        )


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
        # SUPPORT EXISTING PLAIN-TEXT PASSWORDS
        # -------------------------------------------------

        if not password_valid:

            password_valid = (
                password ==
                user.password_hash
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


        # -------------------------------------------------
        # FULL NAME
        # -------------------------------------------------

        full_name = (
            f"{first_name} {last_name}"
        ).strip()

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

            initials = (
                first_name[:2]
            ).upper()

        else:

            initials = (
                user.username[:2]
            ).upper()


        # -------------------------------------------------
        # STORE USER SESSION
        # -------------------------------------------------

        request.session[
            "is_logged_in"
        ] = True

        request.session[
            "user_id"
        ] = user.user_id

        request.session[
            "username"
        ] = user.username

        request.session[
            "first_name"
        ] = first_name

        request.session[
            "last_name"
        ] = last_name

        request.session[
            "full_name"
        ] = full_name

        request.session[
            "email"
        ] = email

        request.session[
            "role"
        ] = role

        request.session[
            "initials"
        ] = initials


        # -------------------------------------------------
        # REMEMBER ME
        # -------------------------------------------------

        if remember:

            # 14 days
            request.session.set_expiry(
                60 * 60 * 24 * 14
            )

        else:

            # Expire when browser closes
            request.session.set_expiry(0)


        # -------------------------------------------------
        # ROLE REDIRECTION
        # -------------------------------------------------

        normalized_role = (
            role.strip().lower()
        )

        if normalized_role in [
            "admin",
            "official"
        ]:

            return redirect(
                "dashboard"
            )

        elif normalized_role == "resident":

            return redirect(
                "home"
            )

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
# FORGOT PASSWORD
# =====================================================

def forgot_password_view(request):

    # =================================================
    # POST REQUEST
    # =================================================

    if request.method == "POST":

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()


        # -------------------------------------------------
        # EMPTY EMAIL
        # -------------------------------------------------

        if not email:

            messages.error(
                request,
                "Please enter your registered email address."
            )

            return render(
                request,
                "login/forgot_password.html"
            )


        # -------------------------------------------------
        # FIND USER BY EMAIL
        # -------------------------------------------------

        try:

            user = User.objects.get(
                email__iexact=email
            )

        except User.DoesNotExist:

            # Generic response prevents account enumeration.

            messages.success(
                request,
                "If an account is registered with that email "
                "address, password reset instructions have "
                "been generated."
            )

            return redirect(
                "forgot_password"
            )

        except User.MultipleObjectsReturned:

            messages.error(
                request,
                "Multiple accounts are using this email "
                "address. Please contact the barangay "
                "administrator."
            )

            return redirect(
                "forgot_password"
            )


        # -------------------------------------------------
        # CHECK ACCOUNT STATUS
        # -------------------------------------------------

        if not user.is_active:

            # Keep response generic.

            messages.success(
                request,
                "If an account is registered with that email "
                "address, password reset instructions have "
                "been generated."
            )

            return redirect(
                "forgot_password"
            )


        # =================================================
        # GENERATE SECURE RESET TOKEN
        # =================================================

        reset_token = secrets.token_urlsafe(
            32
        )


        # -------------------------------------------------
        # STORE RESET INFORMATION IN SESSION
        # -------------------------------------------------

        request.session[
            "password_reset_user_id"
        ] = user.user_id

        request.session[
            "password_reset_email"
        ] = user.email

        request.session[
            "password_reset_token"
        ] = reset_token


        # -------------------------------------------------
        # RESET SESSION EXPIRATION
        # -------------------------------------------------

        # The reset information will expire after 15 minutes.

        request.session.set_expiry(
            60 * 15
        )


        # =================================================
        # CREATE RESET URL
        # =================================================

        # This expects a URL named "reset_password"
        # accepting a token parameter.

        reset_path = reverse(
            "reset_password",
            kwargs={
                "token": reset_token
            }
        )

        reset_url = request.build_absolute_uri(
            reset_path
        )


        # =================================================
        # PREPARE EMAIL
        # =================================================

        first_name = getattr(
            user,
            "first_name",
            ""
        ) or ""

        if first_name:

            greeting = (
                f"Hello {first_name},"
            )

        else:

            greeting = (
                f"Hello {user.username},"
            )


        subject = (
            "BantayBarangay Password Reset"
        )

        email_message = f"""
{greeting}

We received a request to reset the password for your
BantayBarangay account.

Use the link below to reset your password:

{reset_url}

This password reset link is intended to be used within
15 minutes.

If you did not request a password reset, you can ignore
this message.

For your security, never share this reset link with
another person.

BantayBarangay
Secure Digital Governance
"""


        # =================================================
        # SEND EMAIL
        # =================================================

        try:

            send_mail(
                subject=subject,
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[
                    user.email
                ],
                fail_silently=False,
            )

        except Exception as error:

            # Development logging.
            # The email address/password are not printed.

            print(
                "Password reset email error:",
                error
            )

            messages.error(
                request,
                "Unable to generate the password reset "
                "email. Please try again."
            )

            return redirect(
                "forgot_password"
            )


        # =================================================
        # SUCCESS MESSAGE
        # =================================================

        messages.success(
            request,
            "Password reset instructions have been "
            "generated. Check the Django terminal."
        )

        return redirect(
            "forgot_password"
        )


    # =====================================================
    # GET REQUEST
    # =====================================================

    return render(
        request,
        "login/forgot_password.html"
    )


# =====================================================
# LOGOUT
# =====================================================

def logout_view(request):

    # -------------------------------------------------
    # CLEAR ENTIRE SESSION
    # -------------------------------------------------

    request.session.flush()


    # -------------------------------------------------
    # SUCCESS MESSAGE
    # -------------------------------------------------

    messages.success(
        request,
        "You have been successfully signed out."
    )


    # -------------------------------------------------
    # RETURN TO LOGIN
    # -------------------------------------------------

    return redirect(
        "login"
    )