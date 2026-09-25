from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password

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

        # Clear previous session
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
        ).strip()


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
        # NORMALIZE EMAIL
        # -------------------------------------------------

        email = email.lower()


        # -------------------------------------------------
        # FIND USER BY EMAIL
        # -------------------------------------------------

        try:

            user = User.objects.get(
                email__iexact=email
            )

        except User.DoesNotExist:

            # Do not reveal whether an account exists.
            messages.success(
                request,
                "If an account is registered with that email address, "
                "password reset instructions will be provided."
            )

            return render(
                request,
                "login/forgot_password.html"
            )

        except User.MultipleObjectsReturned:

            messages.error(
                request,
                "Multiple accounts are using this email address. "
                "Please contact the barangay administrator."
            )

            return render(
                request,
                "login/forgot_password.html"
            )


        # -------------------------------------------------
        # CHECK ACCOUNT STATUS
        # -------------------------------------------------

        if not user.is_active:

            # Keep response generic so account status
            # is not disclosed publicly.
            messages.success(
                request,
                "If an account is registered with that email address, "
                "password reset instructions will be provided."
            )

            return render(
                request,
                "login/forgot_password.html"
            )


        # =================================================
        # ACCOUNT FOUND
        # =================================================
        #
        # This stores only the minimum information needed
        # for the next reset-password step.
        #
        # Do NOT store the user's current password.
        # =================================================

        request.session[
            "password_reset_user_id"
        ] = user.user_id

        request.session[
            "password_reset_email"
        ] = email


        # -------------------------------------------------
        # SHORT SESSION EXPIRY
        # -------------------------------------------------
        #
        # Temporary recovery session:
        # 15 minutes
        # -------------------------------------------------

        request.session.set_expiry(
            60 * 15
        )


        # -------------------------------------------------
        # SUCCESS MESSAGE
        # -------------------------------------------------

        messages.success(
            request,
            "Your account was found. "
            "You may continue with the password recovery process."
        )


        # -------------------------------------------------
        # CURRENTLY RETURN TO FORGOT PASSWORD PAGE
        # -------------------------------------------------
        #
        # Once reset_password_view is created,
        # change this to:
        #
        # return redirect("reset_password")
        # -------------------------------------------------

        return render(
            request,
            "login/forgot_password.html"
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