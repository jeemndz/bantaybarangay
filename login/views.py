from django.shortcuts import render, redirect
from django.contrib import messages

from .models import User


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        remember = request.POST.get("remember")


        # CHECK EMPTY FIELDS
        if not username or not password:

            messages.error(
                request,
                "Please enter your username and password."
            )

            return render(
                request,
                "login/login.html"
            )


        # FIND USER
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


        # CHECK ACCOUNT STATUS
        if not user.is_active:

            messages.error(
                request,
                "Your account is currently inactive."
            )

            return render(
                request,
                "login/login.html"
            )


        # CHECK NORMAL PASSWORD
        if password != user.password_hash:

            messages.error(
                request,
                "Invalid username or password."
            )

            return render(
                request,
                "login/login.html"
            )


        # STORE SESSION
        request.session["user_id"] = user.user_id
        request.session["username"] = user.username
        request.session["email"] = user.email
        request.session["role"] = user.role


        # REMEMBER ME
        if remember:

            request.session.set_expiry(
                60 * 60 * 24 * 14
            )

        else:

            request.session.set_expiry(0)


        # ROLE-BASED REDIRECT
        if user.role == "admin":

            return redirect("dashboard")

        elif user.role == "official":

            return redirect("dashboard")

        elif user.role == "resident":

            return redirect("home")

        else:

            messages.error(
                request,
                "Your account has an invalid role."
            )

            request.session.flush()

            return render(
                request,
                "login/login.html"
            )


    # GET REQUEST
    return render(
        request,
        "login/login.html"
    )


def logout_view(request):

    request.session.flush()

    return redirect("login")