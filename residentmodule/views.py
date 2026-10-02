from email.mime.image import MIMEImage

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST

from bantaybarangay.security import role_required

from login.models import User
from .models import Resident
from .forms import ResidentForm


# ============================================================
# HELPER: ATTACH ACCOUNT INFORMATION
# ============================================================

def attach_account_information(residents):
    """
    Attach information from the users table to Resident objects.

    Resident.user_id stores the ID of the corresponding
    record in the users table.

    Added attributes:
        resident.account_exists
        resident.account
        resident.account_user_id
        resident.account_username
        resident.account_email
        resident.account_role
        resident.account_is_active
        resident.account_status
    """

    residents = list(residents)

    # --------------------------------------------------------
    # COLLECT USER IDS
    # --------------------------------------------------------

    user_ids = [
        resident.user_id
        for resident in residents
        if resident.user_id is not None
    ]

    # --------------------------------------------------------
    # GET USERS IN ONE QUERY
    # --------------------------------------------------------

    users = User.objects.filter(
        user_id__in=user_ids
    )

    users_by_id = {
        user.user_id: user
        for user in users
    }

    # --------------------------------------------------------
    # ATTACH USER INFORMATION
    # --------------------------------------------------------

    for resident in residents:

        user = users_by_id.get(
            resident.user_id
        )

        # ----------------------------------------------------
        # LINKED ACCOUNT EXISTS
        # ----------------------------------------------------

        if user is not None:

            resident.account_exists = True
            resident.account = user

            resident.account_user_id = (
                user.user_id
            )

            resident.account_username = (
                user.username or ""
            )

            resident.account_email = (
                user.email or ""
            )

            resident.account_role = (
                user.role or ""
            )

            resident.account_is_active = (
                user.is_active is True
            )

            if user.is_active is True:

                resident.account_status = (
                    "Active"
                )

            else:

                resident.account_status = (
                    "Inactive"
                )

        # ----------------------------------------------------
        # NO LINKED ACCOUNT
        # ----------------------------------------------------

        else:

            resident.account_exists = False
            resident.account = None

            resident.account_user_id = None
            resident.account_username = ""
            resident.account_email = ""
            resident.account_role = ""

            resident.account_is_active = False

            resident.account_status = (
                "No Account"
            )

    return residents


# ============================================================
# RESIDENT VERIFICATION EMAIL
# ============================================================

def send_resident_verification_email(resident):
    """
    Send an email notification after a resident
    has been successfully verified.
    """

    # --------------------------------------------------------
    # CHECK RESIDENT EMAIL
    # --------------------------------------------------------

    if not resident.email:

        print(
            "RESIDENT VERIFICATION EMAIL NOT SENT: "
            "Resident has no email address."
        )

        return False

    # --------------------------------------------------------
    # BUILD RESIDENT FULL NAME
    # --------------------------------------------------------

    name_parts = [
        getattr(resident, "first_name", ""),
        getattr(resident, "middle_name", ""),
        getattr(resident, "last_name", ""),
        getattr(resident, "suffix", ""),
    ]

    full_name = " ".join(
        str(part).strip()
        for part in name_parts
        if part
    ).strip()

    if not full_name:
        full_name = "Resident"

    # --------------------------------------------------------
    # EMAIL SUBJECT
    # --------------------------------------------------------

    subject = (
        "BantayBarangay Resident Registration Verified"
    )

    # --------------------------------------------------------
    # PLAIN TEXT VERSION
    # --------------------------------------------------------

    text_content = f"""Hello {full_name},

Your BantayBarangay resident registration has been successfully verified.

Your submitted personal information and verification documents have been reviewed by the barangay.

Verification Status: Verified
Resident ID: {resident.resident_id}

Your resident account is now verified in the BantayBarangay system.

You may now access services available to verified residents using your BantayBarangay account.

If you did not submit this registration or believe you received this message by mistake, please contact your barangay office.

Thank you.

BantayBarangay
Secure Digital Governance
"""

    # --------------------------------------------------------
    # HTML EMAIL VERSION
    # --------------------------------------------------------

    html_content = render_to_string(
        "residentmodule/emails/resident_verified.html",
        {
            "resident": resident,
            "full_name": full_name,
            "verification_status": "Verified",
        }
    )

    # --------------------------------------------------------
    # CREATE EMAIL
    # --------------------------------------------------------

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[resident.email],
        reply_to=[settings.EMAIL_HOST_USER],
    )

    email.attach_alternative(
        html_content,
        "text/html"
    )

    # --------------------------------------------------------
    # ATTACH LOGO
    # --------------------------------------------------------

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

            print(
                "RESIDENT EMAIL LOGO ERROR:",
                repr(error)
            )

    else:

        print(
            "RESIDENT EMAIL LOGO NOT FOUND:",
            logo_path
        )

    # --------------------------------------------------------
    # SEND EMAIL
    # --------------------------------------------------------

    send_result = email.send(
        fail_silently=False
    )

    print(
        "RESIDENT VERIFICATION EMAIL RESULT:",
        send_result
    )

    print(
        "RESIDENT VERIFICATION EMAIL SENT TO:",
        resident.email
    )

    return send_result


# ============================================================
# RESIDENT LIST
# ADMIN + OFFICIAL
# ============================================================

@role_required("admin", "official")
def resident_list(request):

    # --------------------------------------------------------
    # GET RESIDENTS
    # --------------------------------------------------------

    residents = (
        Resident.objects
        .all()
        .order_by("-resident_id")
    )

    # --------------------------------------------------------
    # ATTACH USER ACCOUNT INFORMATION
    # --------------------------------------------------------

    residents = attach_account_information(
        residents
    )

    # --------------------------------------------------------
    # VERIFICATION RESIDENTS
    # --------------------------------------------------------

    verification_residents = [
        resident
        for resident in residents
        if resident.verification_status == "Pending"
    ]

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    total_residents = len(
        residents
    )

    active_accounts = sum(
        1
        for resident in residents
        if resident.account_status == "Active"
    )

    inactive_accounts = sum(
        1
        for resident in residents
        if resident.account_status == "Inactive"
    )

    residents_without_accounts = sum(
        1
        for resident in residents
        if resident.account_status == "No Account"
    )

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {

        "residents":
            residents,

        "verification_residents":
            verification_residents,

        "total_residents":
            total_residents,

        "total_households":
            0,

        "senior_citizens":
            0,

        "pwd_residents":
            0,

        "active_accounts":
            active_accounts,

        "inactive_accounts":
            inactive_accounts,

        "residents_without_accounts":
            residents_without_accounts,
    }

    return render(
        request,
        "residentmodule/resident_list.html",
        context
    )


# ============================================================
# RESIDENT VERIFICATION / REVIEW
# ADMIN + OFFICIAL
# ============================================================

@role_required("admin", "official")
def resident_verify(
    request,
    resident_id
):

    resident = get_object_or_404(
        Resident,
        resident_id=resident_id
    )

    # --------------------------------------------------------
    # ATTACH USER ACCOUNT INFORMATION
    # --------------------------------------------------------

    resident = attach_account_information(
        [resident]
    )[0]

    linked_user = (
        resident.account
    )

    # --------------------------------------------------------
    # PROFILE PICTURE URL
    # --------------------------------------------------------

    profile_picture_url = None

    if resident.profile_picture_path:

        clean_profile_picture_path = (
            str(
                resident.profile_picture_path
            )
            .replace("\\", "/")
            .lstrip("/")
        )

        profile_picture_url = (
            f"{settings.MEDIA_URL}"
            f"{clean_profile_picture_path}"
        )

    # --------------------------------------------------------
    # GOVERNMENT ID URL
    # --------------------------------------------------------

    id_file_url = None
    id_file_is_image = False
    id_file_is_pdf = False

    if resident.id_file_path:

        clean_id_path = (
            str(
                resident.id_file_path
            )
            .replace("\\", "/")
            .lstrip("/")
        )

        id_file_url = (
            f"{settings.MEDIA_URL}"
            f"{clean_id_path}"
        )

        lower_id_path = (
            clean_id_path.lower()
        )

        id_file_is_image = (
            lower_id_path.endswith(
                (
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".webp",
                )
            )
        )

        id_file_is_pdf = (
            lower_id_path.endswith(
                ".pdf"
            )
        )

    # --------------------------------------------------------
    # RESIDENCY DOCUMENT URL
    # --------------------------------------------------------

    residency_file_url = None
    residency_file_is_image = False
    residency_file_is_pdf = False

    if resident.residency_file_path:

        clean_residency_path = (
            str(
                resident.residency_file_path
            )
            .replace("\\", "/")
            .lstrip("/")
        )

        residency_file_url = (
            f"{settings.MEDIA_URL}"
            f"{clean_residency_path}"
        )

        lower_residency_path = (
            clean_residency_path.lower()
        )

        residency_file_is_image = (
            lower_residency_path.endswith(
                (
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".webp",
                )
            )
        )

        residency_file_is_pdf = (
            lower_residency_path.endswith(
                ".pdf"
            )
        )

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {

        "resident":
            resident,

        "linked_user":
            linked_user,

        "account_status":
            resident.account_status,

        "profile_picture_url":
            profile_picture_url,

        "id_file_url":
            id_file_url,

        "id_file_is_image":
            id_file_is_image,

        "id_file_is_pdf":
            id_file_is_pdf,

        "residency_file_url":
            residency_file_url,

        "residency_file_is_image":
            residency_file_is_image,

        "residency_file_is_pdf":
            residency_file_is_pdf,
    }

    return render(
        request,
        "residentmodule/resident_verify.html",
        context
    )


# ============================================================
# ACCEPT RESIDENT
# ADMIN + OFFICIAL
# ============================================================

@role_required("admin", "official")
def accept_resident(
    request,
    resident_id
):

    resident = get_object_or_404(
        Resident,
        resident_id=resident_id
    )

    if request.method != "POST":

        return redirect(
            "resident_verify",
            resident_id=resident_id
        )

    # --------------------------------------------------------
    # ALREADY VERIFIED
    # --------------------------------------------------------

    if resident.verification_status == "Verified":

        messages.warning(
            request,
            "This resident has already been verified."
        )

        return redirect(
            "resident_verify",
            resident_id=resident_id
        )

    # --------------------------------------------------------
    # ALREADY REJECTED
    # --------------------------------------------------------

    if resident.verification_status == "Rejected":

        messages.warning(
            request,
            (
                "This resident registration has "
                "already been rejected."
            )
        )

        return redirect(
            "resident_verify",
            resident_id=resident_id
        )

    # --------------------------------------------------------
    # VERIFY
    # --------------------------------------------------------

    resident.verification_status = (
        "Verified"
    )

    resident.verified_at = (
        timezone.now()
    )

    resident.verified_by = (
        request.session.get(
            "user_id"
        )
    )

    resident.save(
        update_fields=[
            "verification_status",
            "verified_at",
            "verified_by",
        ]
    )

    # --------------------------------------------------------
    # SEND EMAIL
    # --------------------------------------------------------

    if resident.email:

        try:

            send_result = (
                send_resident_verification_email(
                    resident
                )
            )

            if send_result == 1:

                messages.success(
                    request,
                    (
                        "Resident verified successfully. "
                        "The verification email was sent "
                        f"to {resident.email}."
                    )
                )

            else:

                messages.warning(
                    request,
                    (
                        "Resident verified successfully, "
                        "but the email server did not "
                        "confirm the verification email."
                    )
                )

        except Exception as error:

            print(
                "RESIDENT VERIFICATION EMAIL FAILED:",
                repr(error)
            )

            messages.warning(
                request,
                (
                    "Resident verified successfully, "
                    "but the verification email could "
                    "not be sent."
                )
            )

    else:

        messages.warning(
            request,
            (
                "Resident verified successfully, "
                "but this resident does not have a "
                "registered email address."
            )
        )

    return redirect(
        "resident_verify",
        resident_id=resident_id
    )


# ============================================================
# REJECT RESIDENT
# ADMIN + OFFICIAL
# ============================================================

@role_required("admin", "official")
def reject_resident(
    request,
    resident_id
):

    resident = get_object_or_404(
        Resident,
        resident_id=resident_id
    )

    if request.method != "POST":

        return redirect(
            "resident_verify",
            resident_id=resident_id
        )

    # --------------------------------------------------------
    # VERIFIED
    # --------------------------------------------------------

    if resident.verification_status == "Verified":

        messages.warning(
            request,
            (
                "This resident has already been verified "
                "and cannot be rejected from this page."
            )
        )

        return redirect(
            "resident_verify",
            resident_id=resident_id
        )

    # --------------------------------------------------------
    # ALREADY REJECTED
    # --------------------------------------------------------

    if resident.verification_status == "Rejected":

        messages.warning(
            request,
            (
                "This resident registration has already "
                "been rejected."
            )
        )

        return redirect(
            "resident_verify",
            resident_id=resident_id
        )

    # --------------------------------------------------------
    # REJECT
    # --------------------------------------------------------

    resident.verification_status = (
        "Rejected"
    )

    resident.verified_at = (
        timezone.now()
    )

    resident.verified_by = (
        request.session.get(
            "user_id"
        )
    )

    resident.save(
        update_fields=[
            "verification_status",
            "verified_at",
            "verified_by",
        ]
    )

    messages.success(
        request,
        "Resident registration has been rejected."
    )

    return redirect(
        "resident_verify",
        resident_id=resident_id
    )


# ============================================================
# CREATE RESIDENT
# ADMIN + OFFICIAL
# ============================================================

@role_required("admin", "official")
def resident_create(request):

    if request.method == "POST":

        form = ResidentForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Resident added successfully."
            )

            return redirect(
                "resident_list"
            )

    else:

        form = ResidentForm()

    context = {

        "form":
            form,

        "page_title":
            "Add Resident",

        "page_description":
            (
                "Register a new resident "
                "in the barangay records."
            ),
    }

    return render(
        request,
        "residentmodule/resident_form.html",
        context
    )


# ============================================================
# UPDATE RESIDENT
# ADMIN + OFFICIAL
# ============================================================

@role_required("admin", "official")
def resident_update(
    request,
    resident_id
):

    resident = get_object_or_404(
        Resident,
        resident_id=resident_id
    )

    if request.method == "POST":

        form = ResidentForm(
            request.POST,
            instance=resident
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                (
                    "Resident information updated "
                    "successfully."
                )
            )

            return redirect(
                "resident_list"
            )

    else:

        form = ResidentForm(
            instance=resident
        )

    context = {

        "form":
            form,

        "resident":
            resident,

        "page_title":
            "Edit Resident",

        "page_description":
            "Update the resident information.",
    }

    return render(
        request,
        "residentmodule/resident_form.html",
        context
    )


# ============================================================
# TOGGLE RESIDENT ACCOUNT STATUS
# ADMIN + OFFICIAL
# ============================================================

@role_required("admin", "official")
@require_POST
def toggle_resident_account_status(
    request,
    resident_id
):

    # --------------------------------------------------------
    # GET RESIDENT
    # --------------------------------------------------------

    resident = get_object_or_404(
        Resident,
        resident_id=resident_id
    )

    # --------------------------------------------------------
    # RESIDENT MUST HAVE USER ID
    # --------------------------------------------------------

    if resident.user_id is None:

        messages.error(
            request,
            (
                "This resident does not have "
                "a linked user account."
            )
        )

        return redirect(
            "resident_list"
        )

    # --------------------------------------------------------
    # GET USER ACCOUNT
    # --------------------------------------------------------

    user = (
        User.objects
        .filter(
            user_id=resident.user_id
        )
        .first()
    )

    if user is None:

        messages.error(
            request,
            (
                "The user account linked to this "
                "resident could not be found."
            )
        )

        return redirect(
            "resident_list"
        )

    # --------------------------------------------------------
    # TOGGLE ACCOUNT
    # --------------------------------------------------------

    current_status = bool(
        user.is_active
    )

    user.is_active = (
        not current_status
    )

    user.save(
        update_fields=[
            "is_active"
        ]
    )

    # --------------------------------------------------------
    # MESSAGE
    # --------------------------------------------------------

    resident_name = (
        f"{resident.first_name} "
        f"{resident.last_name}"
    ).strip()

    if user.is_active:

        messages.success(
            request,
            (
                f"{resident_name}'s account "
                "has been activated."
            )
        )

    else:

        messages.success(
            request,
            (
                f"{resident_name}'s account "
                "has been deactivated."
            )
        )

    return redirect(
        "resident_list"
    )


# ============================================================
# DELETE RESIDENT
# ADMIN + OFFICIAL
# ============================================================

@role_required("admin", "official")
def resident_delete(
    request,
    resident_id
):

    resident = get_object_or_404(
        Resident,
        resident_id=resident_id
    )

    if request.method == "POST":

        resident.delete()

        messages.success(
            request,
            "Resident deleted successfully."
        )

        return redirect(
            "resident_list"
        )

    return render(
        request,
        "residentmodule/resident_confirm_delete.html",
        {
            "resident":
                resident
        }
    )