from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


# =========================================================
# LOGIN REQUIRED
# =========================================================

def session_login_required(view_function):

    @wraps(view_function)
    def wrapper(request, *args, **kwargs):

        if not request.session.get(
            "is_logged_in"
        ):

            return redirect(
                "login"
            )

        return view_function(
            request,
            *args,
            **kwargs
        )

    return wrapper


# =========================================================
# ROLE REQUIRED
# =========================================================

def role_required(*allowed_roles):

    normalized_roles = {
        str(role).strip().lower()
        for role in allowed_roles
    }

    def decorator(view_function):

        @wraps(view_function)
        def wrapper(
            request,
            *args,
            **kwargs
        ):

            # ---------------------------------------------
            # NOT LOGGED IN
            # ---------------------------------------------

            if not request.session.get(
                "is_logged_in"
            ):

                return redirect(
                    "login"
                )


            # ---------------------------------------------
            # CURRENT ROLE
            # ---------------------------------------------

            role = (
                request.session.get(
                    "role",
                    ""
                )
                or ""
            ).strip().lower()


            # ---------------------------------------------
            # AUTHORIZED
            # ---------------------------------------------

            if role in normalized_roles:

                return view_function(
                    request,
                    *args,
                    **kwargs
                )


            # ---------------------------------------------
            # UNAUTHORIZED
            # ---------------------------------------------

            messages.error(
                request,
                (
                    "You do not have permission "
                    "to access that page."
                )
            )


            if role == "resident":

                return redirect(
                    "home"
                )


            if role in {
                "admin",
                "official",
            }:

                return redirect(
                    "dashboard"
                )


            return redirect(
                "login"
            )

        return wrapper

    return decorator