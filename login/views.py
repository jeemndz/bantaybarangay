import hashlib
import secrets

from datetime import timedelta
from email.mime.image import MIMEImage

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import (
    check_password,
    make_password,
)
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone

from .models import User, PasswordResetToken
from auditlogs.utils import create_audit_log


# =========================================================
# PASSWORD RESET SETTINGS
# =========================================================

RESET_CODE_EXPIRY_MINUTES = 10


# =========================================================
# PASSWORD RESET HELPERS
# =========================================================

def generate_reset_code():
    """
    Generate a cryptographically secure 6-digit code.
    """

    return f"{secrets.randbelow(1_000_000):06d}"


def hash_reset_code(code):
    """
    Hash the verification code before storing it.
    """

    return hashlib.sha256(
        code.encode("utf-8")
    ).hexdigest()


def mask_email(email):
    """
    Example:
    example@gmail.com -> e*****e@gmail.com
    """

    if not email or "@" not in email:
        return ""

    local_part, domain = email.split("@", 1)

    if len(local_part) <= 1:

        masked_local = "*"

    elif len(local_part) == 2:

        masked_local = (
            local_part[0]
            + "*"
        )

    else:

        masked_local = (
            local_part[0]
            + ("*" * (len(local_part) - 2))
            + local_part[-1]
        )

    return f"{masked_local}@{domain}"


def clear_password_reset_session(request):
    """
    Remove password reset data from session.
    """

    request.session.pop(
        "password_reset_user_id",
        None
    )

    request.session.pop(
        "password_reset_id",
        None
    )

    request.session.pop(
        "password_reset_verified",
        None
    )


# =========================================================
# SEND PASSWORD RESET EMAIL
# =========================================================

def send_reset_code_email(user, code):
    """
    Send password reset verification code
    as both plain text and HTML.

    Compatible with Django 6.
    """

    # -----------------------------------------------------
    # VALIDATE EMAIL
    # -----------------------------------------------------

    if not user.email:

        raise ValueError(
            "The user does not have an email address."
        )

    # -----------------------------------------------------
    # SUBJECT
    # -----------------------------------------------------

    subject = (
        "BantayBarangay Password Reset Code"
    )

    # -----------------------------------------------------
    # PLAIN TEXT VERSION
    # -----------------------------------------------------

    text_content = f"""Hello {user.username},

We received a request to reset the password for your BantayBarangay account.

Your verification code is:

{code}

This code expires in {RESET_CODE_EXPIRY_MINUTES} minutes.

Do not share this verification code with anyone.

BantayBarangay staff will never ask you for your verification code.

If you did not request a password reset, you can ignore this email.
Your password will remain unchanged.

BantayBarangay
Secure Digital Governance
"""

    # -----------------------------------------------------
    # HTML VERSION
    # -----------------------------------------------------

    html_content = render_to_string(
        "login/emails/password_reset_code.html",
        {
            "username":
                user.username,

            "code":
                code,

            "expiry_minutes":
                RESET_CODE_EXPIRY_MINUTES,
        }
    )

    # -----------------------------------------------------
    # CREATE EMAIL
    # -----------------------------------------------------

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[
            user.email
        ],
        reply_to=[
            settings.EMAIL_HOST_USER
        ],
    )

    # IMPORTANT:
    # Do NOT use:
    #
    # email.mixed_subtype = "related"
    #
    # Django 6 no longer supports that
    # undocumented attribute.

    # -----------------------------------------------------
    # ATTACH HTML VERSION
    # -----------------------------------------------------

    email.attach_alternative(
        html_content,
        "text/html"
    )

    # -----------------------------------------------------
    # EMBED BANTAYBARANGAY LOGO
    # -----------------------------------------------------

    logo_path = (
        settings.BASE_DIR
        / "static"
        / "images"
        / "SYSTEMS_LOGO.png"
    )

    if logo_path.exists():

        try:

            with open(
                logo_path,
                "rb"
            ) as logo_file:

                logo_image = MIMEImage(
                    logo_file.read(),
                    _subtype="png"
                )

                logo_image.add_header(
                    "Content-ID",
                    "<bantaybarangay_logo>"
                )

                logo_image.add_header(
                    "Content-Disposition",
                    "inline",
                    filename="SYSTEMS_LOGO.png"
                )

                email.attach(
                    logo_image
                )

        except Exception as error:

            # Logo failure should not prevent
            # the reset code from being sent.

            print(
                "PASSWORD RESET EMAIL LOGO ERROR:",
                repr(error)
            )

    else:

        print(
            "PASSWORD RESET EMAIL LOGO NOT FOUND:",
            logo_path
        )

    # -----------------------------------------------------
    # SAFE EMAIL CONFIGURATION DEBUG
    # -----------------------------------------------------

    print("=" * 70)

    print(
        "EMAIL HOST:",
        getattr(
            settings,
            "EMAIL_HOST",
            None
        )
    )

    print(
        "EMAIL PORT:",
        getattr(
            settings,
            "EMAIL_PORT",
            None
        )
    )

    print(
        "EMAIL TLS:",
        getattr(
            settings,
            "EMAIL_USE_TLS",
            None
        )
    )

    print(
        "EMAIL USER:",
        getattr(
            settings,
            "EMAIL_HOST_USER",
            None
        )
    )

    print(
        "EMAIL PASSWORD CONFIGURED:",
        bool(
            getattr(
                settings,
                "EMAIL_HOST_PASSWORD",
                None
            )
        )
    )

    print(
        "PASSWORD RESET RECIPIENT:",
        user.email
    )

    print("=" * 70)

    # -----------------------------------------------------
    # SEND EMAIL
    # -----------------------------------------------------

    result = email.send(
        fail_silently=False
    )

    print(
        "PASSWORD RESET EMAIL RESULT:",
        result
    )

    return result


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    # -----------------------------------------------------
    # ALREADY LOGGED IN
    # -----------------------------------------------------

    if request.session.get("is_logged_in"):

        role = request.session.get(
            "role"
        )

        if role in [
            "admin",
            "official",
        ]:

            return redirect(
                "dashboard"
            )

        return redirect(
            "home"
        )

    # -----------------------------------------------------
    # LOGIN SUBMISSION
    # -----------------------------------------------------

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

        except (
            User.DoesNotExist,
            User.MultipleObjectsReturned,
        ):

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

        password_valid = check_password(
            password,
            user.password_hash
        )

        # -------------------------------------------------
        # LEGACY PLAINTEXT SUPPORT
        # -------------------------------------------------

        if not password_valid:

            password_valid = (
                password
                == user.password_hash
            )

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
        # LOGIN SUCCESS
        # -------------------------------------------------

        request.session.flush()

        # -------------------------------------------------
        # USER INFORMATION
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

        if not full_name:

            full_name = (
                user.username
            )

        # -------------------------------------------------
        # INITIALS
        # -------------------------------------------------

        initials = ""

        if first_name:

            initials += (
                first_name[0].upper()
            )

        if last_name:

            initials += (
                last_name[0].upper()
            )

        if not initials:

            initials = (
                user.username[:2].upper()
            )

        # -------------------------------------------------
        # SESSION DATA
        # -------------------------------------------------

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
        ] = user.email or ""

        request.session[
            "role"
        ] = user.role

        request.session[
            "initials"
        ] = initials

        request.session[
            "is_logged_in"
        ] = True

        # -------------------------------------------------
        # REMEMBER ME
        # -------------------------------------------------

        if remember:

            request.session.set_expiry(
                60 * 60 * 24 * 14
            )

        else:

            request.session.set_expiry(
                0
            )

        # -------------------------------------------------
        # AUDIT LOG
        # -------------------------------------------------

        try:

            create_audit_log(
                request=request,
                action="LOGIN",
                description=(
                    f"User {user.username} "
                    "logged in."
                )
            )

        except Exception as error:

            print(
                "LOGIN AUDIT LOG ERROR:",
                repr(error)
            )

        # -------------------------------------------------
        # REDIRECT
        # -------------------------------------------------

        if user.role in [
            "admin",
            "official",
        ]:

            return redirect(
                "dashboard"
            )

        return redirect(
            "home"
        )

    return render(
        request,
        "login/login.html"
    )


# =========================================================
# FORGOT PASSWORD
# =========================================================

def forgot_password_view(request):

    if request.method == "POST":

        email_address = request.POST.get(
            "email",
            ""
        ).strip().lower()

        # -------------------------------------------------
        # EMPTY EMAIL
        # -------------------------------------------------

        if not email_address:

            messages.error(
                request,
                "Please enter your email address."
            )

            return render(
                request,
                "login/forgot_password.html"
            )

        # -------------------------------------------------
        # FIND USER
        # -------------------------------------------------

        try:

            user = User.objects.get(
                email__iexact=email_address
            )

        except (
            User.DoesNotExist,
            User.MultipleObjectsReturned,
        ):

            messages.success(
                request,
                (
                    "If the email address is registered, "
                    "a verification code will be sent."
                )
            )

            return redirect(
                "forgot_password"
            )

        # -------------------------------------------------
        # CHECK ACCOUNT
        # -------------------------------------------------

        if (
            not user.is_active
            or not user.email
        ):

            messages.success(
                request,
                (
                    "If the email address is registered, "
                    "a verification code will be sent."
                )
            )

            return redirect(
                "forgot_password"
            )

        # -------------------------------------------------
        # GENERATE CODE
        # -------------------------------------------------

        code = generate_reset_code()

        code_hash = hash_reset_code(
            code
        )

        expires_at = (
            timezone.now()
            + timedelta(
                minutes=
                    RESET_CODE_EXPIRY_MINUTES
            )
        )

        # -------------------------------------------------
        # INVALIDATE OLD UNUSED CODES
        # -------------------------------------------------

        PasswordResetToken.objects.filter(
            user_id=user.user_id,
            used=False
        ).update(
            used=True
        )

        # -------------------------------------------------
        # CREATE NEW RESET RECORD
        # -------------------------------------------------

        reset_record = (
            PasswordResetToken.objects.create(
                user_id=user.user_id,
                token_hash=code_hash,
                expires_at=expires_at,
                used=False,
            )
        )

        # -------------------------------------------------
        # SEND EMAIL
        # -------------------------------------------------

        try:

            send_result = (
                send_reset_code_email(
                    user,
                    code
                )
            )

            print(
                "PASSWORD RESET EMAIL RESULT:",
                send_result
            )

            print(
                "PASSWORD RESET EMAIL SENT TO:",
                user.email
            )

        except Exception as error:

            # Remove the token because the email
            # was not successfully sent.

            reset_record.delete()

            print("=" * 70)

            print(
                "PASSWORD RESET EMAIL FAILED"
            )

            print(
                "ERROR TYPE:",
                type(error).__name__
            )

            print(
                "ERROR MESSAGE:",
                str(error)
            )

            print(
                "ERROR REPR:",
                repr(error)
            )

            print("=" * 70)

            messages.error(
                request,
                (
                    "Unable to send the verification "
                    "code. Please try again later."
                )
            )

            return render(
                request,
                "login/forgot_password.html"
            )

        # -------------------------------------------------
        # VERIFY SEND RESULT
        # -------------------------------------------------

        if send_result != 1:

            reset_record.delete()

            print(
                "PASSWORD RESET EMAIL SERVER "
                "DID NOT CONFIRM DELIVERY."
            )

            messages.error(
                request,
                (
                    "Unable to send the verification "
                    "code. Please try again later."
                )
            )

            return render(
                request,
                "login/forgot_password.html"
            )

        # -------------------------------------------------
        # SESSION
        # -------------------------------------------------

        request.session[
            "password_reset_user_id"
        ] = user.user_id

        request.session[
            "password_reset_id"
        ] = reset_record.reset_id

        request.session[
            "password_reset_verified"
        ] = False

        request.session.set_expiry(
            RESET_CODE_EXPIRY_MINUTES
            * 60
        )

        # -------------------------------------------------
        # SUCCESS MESSAGE
        # -------------------------------------------------

        messages.success(
            request,
            (
                "A 6-digit verification code was sent "
                f"to {mask_email(user.email)}."
            )
        )

        # -------------------------------------------------
        # AUDIT LOG
        # -------------------------------------------------

        try:

            create_audit_log(
                request=request,
                action=(
                    "PASSWORD_RESET_REQUEST"
                ),
                description=(
                    "Password reset verification "
                    "code requested for "
                    f"{user.username}."
                )
            )

        except Exception as error:

            print(
                "PASSWORD RESET AUDIT ERROR:",
                repr(error)
            )

        return redirect(
            "verify_reset_code"
        )

    return render(
        request,
        "login/forgot_password.html"
    )


# =========================================================
# VERIFY RESET CODE
# =========================================================

def verify_reset_code_view(request):

    user_id = request.session.get(
        "password_reset_user_id"
    )

    reset_id = request.session.get(
        "password_reset_id"
    )

    # -----------------------------------------------------
    # CHECK SESSION
    # -----------------------------------------------------

    if not user_id or not reset_id:

        messages.error(
            request,
            (
                "Your password reset session has expired. "
                "Please request a new code."
            )
        )

        clear_password_reset_session(
            request
        )

        return redirect(
            "forgot_password"
        )

    # -----------------------------------------------------
    # FIND USER
    # -----------------------------------------------------

    try:

        user = User.objects.get(
            user_id=user_id,
            is_active=True
        )

    except User.DoesNotExist:

        clear_password_reset_session(
            request
        )

        messages.error(
            request,
            (
                "Unable to verify your account. "
                "Please request a new code."
            )
        )

        return redirect(
            "forgot_password"
        )

    # -----------------------------------------------------
    # FIND RESET RECORD
    # -----------------------------------------------------

    try:

        reset_record = (
            PasswordResetToken.objects.get(
                reset_id=reset_id,
                user_id=user_id,
                used=False,
            )
        )

    except PasswordResetToken.DoesNotExist:

        clear_password_reset_session(
            request
        )

        messages.error(
            request,
            (
                "This verification code is no longer "
                "valid. Please request a new code."
            )
        )

        return redirect(
            "forgot_password"
        )

    # -----------------------------------------------------
    # CHECK EXPIRATION
    # -----------------------------------------------------

    if (
        timezone.now()
        >= reset_record.expires_at
    ):

        reset_record.used = True

        reset_record.save(
            update_fields=[
                "used"
            ]
        )

        clear_password_reset_session(
            request
        )

        messages.error(
            request,
            (
                "Your verification code has expired. "
                "Please request a new one."
            )
        )

        return redirect(
            "forgot_password"
        )

    # -----------------------------------------------------
    # VERIFY SUBMITTED CODE
    # -----------------------------------------------------

    if request.method == "POST":

        code = request.POST.get(
            "code",
            ""
        ).strip()

        # -------------------------------------------------
        # CODE FORMAT
        # -------------------------------------------------

        if (
            len(code) != 6
            or not code.isdigit()
        ):

            messages.error(
                request,
                (
                    "Please enter the complete "
                    "6-digit verification code."
                )
            )

            return render(
                request,
                "login/verify_reset_code.html",
                {
                    "masked_email":
                        mask_email(
                            user.email
                        )
                }
            )

        # -------------------------------------------------
        # HASH CODE
        # -------------------------------------------------

        submitted_hash = (
            hash_reset_code(
                code
            )
        )

        # -------------------------------------------------
        # COMPARE CODE
        # -------------------------------------------------

        code_valid = (
            secrets.compare_digest(
                submitted_hash,
                reset_record.token_hash
            )
        )

        if not code_valid:

            messages.error(
                request,
                (
                    "The verification code you "
                    "entered is incorrect."
                )
            )

            return render(
                request,
                "login/verify_reset_code.html",
                {
                    "masked_email":
                        mask_email(
                            user.email
                        )
                }
            )

        # -------------------------------------------------
        # VERIFIED
        # -------------------------------------------------

        request.session[
            "password_reset_verified"
        ] = True

        request.session.set_expiry(
            RESET_CODE_EXPIRY_MINUTES
            * 60
        )

        # -------------------------------------------------
        # AUDIT LOG
        # -------------------------------------------------

        try:

            create_audit_log(
                request=request,
                action=(
                    "PASSWORD_RESET_CODE_VERIFIED"
                ),
                description=(
                    "Password reset verification "
                    "code verified for "
                    f"{user.username}."
                )
            )

        except Exception as error:

            print(
                "PASSWORD RESET VERIFY "
                "AUDIT ERROR:",
                repr(error)
            )

        return redirect(
            "reset_password"
        )

    return render(
        request,
        "login/verify_reset_code.html",
        {
            "masked_email":
                mask_email(
                    user.email
                )
        }
    )


# =========================================================
# RESEND RESET CODE
# =========================================================

def resend_reset_code_view(request):

    if request.method != "POST":

        return redirect(
            "verify_reset_code"
        )

    user_id = request.session.get(
        "password_reset_user_id"
    )

    # -----------------------------------------------------
    # CHECK SESSION
    # -----------------------------------------------------

    if not user_id:

        messages.error(
            request,
            "Your password reset session has expired."
        )

        return redirect(
            "forgot_password"
        )

    # -----------------------------------------------------
    # FIND USER
    # -----------------------------------------------------

    try:

        user = User.objects.get(
            user_id=user_id,
            is_active=True
        )

    except User.DoesNotExist:

        clear_password_reset_session(
            request
        )

        messages.error(
            request,
            (
                "Unable to resend the verification code. "
                "Please start again."
            )
        )

        return redirect(
            "forgot_password"
        )

    if not user.email:

        clear_password_reset_session(
            request
        )

        messages.error(
            request,
            (
                "No email address is associated "
                "with this account."
            )
        )

        return redirect(
            "forgot_password"
        )

    # -----------------------------------------------------
    # INVALIDATE OLD CODE
    # -----------------------------------------------------

    PasswordResetToken.objects.filter(
        user_id=user.user_id,
        used=False
    ).update(
        used=True
    )

    # -----------------------------------------------------
    # GENERATE NEW CODE
    # -----------------------------------------------------

    code = generate_reset_code()

    code_hash = hash_reset_code(
        code
    )

    expires_at = (
        timezone.now()
        + timedelta(
            minutes=
                RESET_CODE_EXPIRY_MINUTES
        )
    )

    # -----------------------------------------------------
    # CREATE RESET RECORD
    # -----------------------------------------------------

    reset_record = (
        PasswordResetToken.objects.create(
            user_id=user.user_id,
            token_hash=code_hash,
            expires_at=expires_at,
            used=False,
        )
    )

    # -----------------------------------------------------
    # SEND EMAIL
    # -----------------------------------------------------

    try:

        send_result = (
            send_reset_code_email(
                user,
                code
            )
        )

        print(
            "PASSWORD RESET RESEND RESULT:",
            send_result
        )

        print(
            "PASSWORD RESET CODE RESENT TO:",
            user.email
        )

    except Exception as error:

        reset_record.delete()

        print("=" * 70)

        print(
            "PASSWORD RESET RESEND "
            "EMAIL FAILED"
        )

        print(
            "ERROR TYPE:",
            type(error).__name__
        )

        print(
            "ERROR MESSAGE:",
            str(error)
        )

        print(
            "ERROR REPR:",
            repr(error)
        )

        print("=" * 70)

        messages.error(
            request,
            (
                "Unable to resend the verification "
                "code. Please try again later."
            )
        )

        return redirect(
            "verify_reset_code"
        )

    # -----------------------------------------------------
    # VERIFY SEND RESULT
    # -----------------------------------------------------

    if send_result != 1:

        reset_record.delete()

        messages.error(
            request,
            (
                "Unable to resend the verification "
                "code. Please try again later."
            )
        )

        return redirect(
            "verify_reset_code"
        )

    # -----------------------------------------------------
    # UPDATE SESSION
    # -----------------------------------------------------

    request.session[
        "password_reset_id"
    ] = reset_record.reset_id

    request.session[
        "password_reset_verified"
    ] = False

    request.session.set_expiry(
        RESET_CODE_EXPIRY_MINUTES
        * 60
    )

    # -----------------------------------------------------
    # SUCCESS MESSAGE
    # -----------------------------------------------------

    messages.success(
        request,
        (
            "A new verification code was sent "
            f"to {mask_email(user.email)}."
        )
    )

    # -----------------------------------------------------
    # AUDIT LOG
    # -----------------------------------------------------

    try:

        create_audit_log(
            request=request,
            action=(
                "PASSWORD_RESET_CODE_RESENT"
            ),
            description=(
                "A new password reset verification "
                "code was sent for "
                f"{user.username}."
            )
        )

    except Exception as error:

        print(
            "PASSWORD RESET RESEND "
            "AUDIT ERROR:",
            repr(error)
        )

    return redirect(
        "verify_reset_code"
    )


# =========================================================
# RESET PASSWORD
# =========================================================

def reset_password_view(request):

    user_id = request.session.get(
        "password_reset_user_id"
    )

    reset_id = request.session.get(
        "password_reset_id"
    )

    verified = request.session.get(
        "password_reset_verified"
    )

    # -----------------------------------------------------
    # REQUIRE VERIFICATION
    # -----------------------------------------------------

    if (
        not user_id
        or not reset_id
        or verified is not True
    ):

        messages.error(
            request,
            (
                "Please verify your password reset "
                "code first."
            )
        )

        return redirect(
            "forgot_password"
        )

    # -----------------------------------------------------
    # FIND RESET RECORD
    # -----------------------------------------------------

    try:

        reset_record = (
            PasswordResetToken.objects.get(
                reset_id=reset_id,
                user_id=user_id,
                used=False,
            )
        )

    except PasswordResetToken.DoesNotExist:

        clear_password_reset_session(
            request
        )

        messages.error(
            request,
            (
                "Your password reset request "
                "is no longer valid."
            )
        )

        return redirect(
            "forgot_password"
        )

    # -----------------------------------------------------
    # CHECK EXPIRATION
    # -----------------------------------------------------

    if (
        timezone.now()
        >= reset_record.expires_at
    ):

        reset_record.used = True

        reset_record.save(
            update_fields=[
                "used"
            ]
        )

        clear_password_reset_session(
            request
        )

        messages.error(
            request,
            (
                "Your password reset session has expired. "
                "Please request a new verification code."
            )
        )

        return redirect(
            "forgot_password"
        )

    # -----------------------------------------------------
    # FIND USER
    # -----------------------------------------------------

    try:

        user = User.objects.get(
            user_id=user_id,
            is_active=True
        )

    except User.DoesNotExist:

        clear_password_reset_session(
            request
        )

        messages.error(
            request,
            (
                "Unable to reset the password "
                "for this account."
            )
        )

        return redirect(
            "forgot_password"
        )

    # -----------------------------------------------------
    # PASSWORD SUBMISSION
    # -----------------------------------------------------

    if request.method == "POST":

        new_password = request.POST.get(
            "new_password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        # -------------------------------------------------
        # EMPTY PASSWORD
        # -------------------------------------------------

        if (
            not new_password
            or not confirm_password
        ):

            messages.error(
                request,
                (
                    "Please enter and confirm "
                    "your new password."
                )
            )

            return render(
                request,
                "login/reset_password.html",
                {
                    "username":
                        user.username
                }
            )

        # -------------------------------------------------
        # PASSWORDS MUST MATCH
        # -------------------------------------------------

        if (
            new_password
            != confirm_password
        ):

            messages.error(
                request,
                "The passwords do not match."
            )

            return render(
                request,
                "login/reset_password.html",
                {
                    "username":
                        user.username
                }
            )

        # -------------------------------------------------
        # MINIMUM LENGTH
        # -------------------------------------------------

        if len(new_password) < 8:

            messages.error(
                request,
                (
                    "Your new password must be "
                    "at least 8 characters long."
                )
            )

            return render(
                request,
                "login/reset_password.html",
                {
                    "username":
                        user.username
                }
            )

        # -------------------------------------------------
        # PREVENT PASSWORD REUSE
        # -------------------------------------------------

        same_as_current = check_password(
            new_password,
            user.password_hash
        )

        # Legacy plaintext support.

        if not same_as_current:

            same_as_current = (
                new_password
                == user.password_hash
            )

        if same_as_current:

            messages.error(
                request,
                (
                    "Your new password must be different "
                    "from your current password."
                )
            )

            return render(
                request,
                "login/reset_password.html",
                {
                    "username":
                        user.username
                }
            )

        # -------------------------------------------------
        # SAVE HASHED PASSWORD
        # -------------------------------------------------

        user.password_hash = (
            make_password(
                new_password
            )
        )

        user.save(
            update_fields=[
                "password_hash"
            ]
        )

        # -------------------------------------------------
        # MARK TOKEN USED
        # -------------------------------------------------

        reset_record.used = True

        reset_record.save(
            update_fields=[
                "used"
            ]
        )

        # -------------------------------------------------
        # INVALIDATE OTHER TOKENS
        # -------------------------------------------------

        PasswordResetToken.objects.filter(
            user_id=user.user_id,
            used=False
        ).update(
            used=True
        )

        # -------------------------------------------------
        # AUDIT LOG
        # -------------------------------------------------

        try:

            create_audit_log(
                request=request,
                action="PASSWORD_RESET",
                description=(
                    "Password successfully reset "
                    f"for {user.username}."
                )
            )

        except Exception as error:

            print(
                "PASSWORD RESET AUDIT ERROR:",
                repr(error)
            )

        # -------------------------------------------------
        # CLEAR SESSION
        # -------------------------------------------------

        clear_password_reset_session(
            request
        )

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        messages.success(
            request,
            (
                "Your password has been reset "
                "successfully. Please log in "
                "using your new password."
            )
        )

        return redirect(
            "login"
        )

    return render(
        request,
        "login/reset_password.html",
        {
            "username":
                user.username
        }
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    username = request.session.get(
        "username"
    )

    # -----------------------------------------------------
    # AUDIT LOG
    # -----------------------------------------------------

    if username:

        try:

            create_audit_log(
                request=request,
                action="LOGOUT",
                description=(
                    f"User {username} "
                    "logged out."
                )
            )

        except Exception as error:

            print(
                "LOGOUT AUDIT ERROR:",
                repr(error)
            )

    # -----------------------------------------------------
    # CLEAR SESSION
    # -----------------------------------------------------

    request.session.flush()

    return redirect(
        "login"
    )