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

from bantaybarangay.security import role_required

from .models import Resident
from .forms import ResidentForm


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

    # --------------------------------------------------------
    # ATTACH HTML VERSION
    #
    # Django 6:
    # Do NOT use email.mixed_subtype = "related".
    # --------------------------------------------------------

    email.attach_alternative(
        html_content,
        "text/html"
    )

    # --------------------------------------------------------
    # ATTACH BANTAYBARANGAY LOGO
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

            # A logo problem should not stop the email.

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
    # SAFE EMAIL DEBUG INFORMATION
    # --------------------------------------------------------

    print("=" * 70)
    print("RESIDENT VERIFICATION EMAIL")

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
        "RESIDENT EMAIL RECIPIENT:",
        resident.email
    )

    print("=" * 70)

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

    residents = (
        Resident.objects
        .all()
        .order_by("-resident_id")
    )

    verification_residents = (
        Resident.objects
        .filter(
            verification_status="Pending"
        )
        .order_by("-resident_id")
    )

    context = {
        "residents": residents,
        "verification_residents": verification_residents,
        "total_residents": residents.count(),
        "total_households": 0,
        "senior_citizens": 0,
        "pwd_residents": 0,
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
        "resident": resident,

        # Profile picture
        "profile_picture_url":
            profile_picture_url,

        # Government ID
        "id_file_url":
            id_file_url,

        "id_file_is_image":
            id_file_is_image,

        "id_file_is_pdf":
            id_file_is_pdf,

        # Proof of residency
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

    # --------------------------------------------------------
    # ONLY ACCEPT POST REQUESTS
    # --------------------------------------------------------

    if request.method != "POST":

        return redirect(
            "resident_verify",
            resident_id=resident_id
        )

    # --------------------------------------------------------
    # PREVENT DUPLICATE VERIFICATION
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
    # PREVENT REJECTED RESIDENT FROM BEING ACCEPTED
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
    # VERIFY RESIDENT
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

    # --------------------------------------------------------
    # SAVE VERIFICATION
    # --------------------------------------------------------

    resident.save(
        update_fields=[
            "verification_status",
            "verified_at",
            "verified_by",
        ]
    )

    print(
        "RESIDENT VERIFIED:",
        resident.resident_id
    )

    print(
        "RESIDENT EMAIL:",
        resident.email
    )

    # --------------------------------------------------------
    # SEND VERIFICATION EMAIL
    # --------------------------------------------------------

    if resident.email:

        try:

            send_result = (
                send_resident_verification_email(
                    resident
                )
            )

            # ------------------------------------------------
            # EMAIL ACCEPTED BY EMAIL BACKEND
            # ------------------------------------------------

            if send_result == 1:

                messages.success(
                    request,
                    (
                        "Resident verified successfully. "
                        "The verification email was sent "
                        f"to {resident.email}."
                    )
                )

            # ------------------------------------------------
            # EMAIL BACKEND DID NOT CONFIRM SEND
            # ------------------------------------------------

            else:

                print(
                    "RESIDENT EMAIL SEND RESULT:",
                    send_result
                )

                messages.warning(
                    request,
                    (
                        "Resident verified successfully, "
                        "but the email server did not "
                        "confirm the verification email."
                    )
                )

        # ----------------------------------------------------
        # EMAIL FAILED
        # ----------------------------------------------------

        except Exception as error:

            print("=" * 70)
            print(
                "RESIDENT VERIFICATION EMAIL FAILED"
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

            print(
                "RESIDENT ID:",
                resident.resident_id
            )

            print(
                "RESIDENT EMAIL:",
                resident.email
            )

            print("=" * 70)

            messages.warning(
                request,
                (
                    "Resident verified successfully, "
                    "but the verification email could "
                    "not be sent."
                )
            )

    # --------------------------------------------------------
    # RESIDENT HAS NO EMAIL
    # --------------------------------------------------------

    else:

        print(
            "RESIDENT VERIFICATION EMAIL NOT SENT: "
            "No resident email address."
        )

        messages.warning(
            request,
            (
                "Resident verified successfully, "
                "but this resident does not have a "
                "registered email address."
            )
        )

    # --------------------------------------------------------
    # RETURN TO VERIFICATION PAGE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # ONLY ACCEPT POST REQUESTS
    # --------------------------------------------------------

    if request.method != "POST":

        return redirect(
            "resident_verify",
            resident_id=resident_id
        )

    # --------------------------------------------------------
    # PREVENT VERIFIED RESIDENT FROM BEING REJECTED
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
    # PREVENT DUPLICATE REJECTION
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
    # REJECT RESIDENT
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

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    resident.save(
        update_fields=[
            "verification_status",
            "verified_at",
            "verified_by",
        ]
    )

    # --------------------------------------------------------
    # SUCCESS MESSAGE
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    if request.method == "POST":

        resident.delete()

        messages.success(
            request,
            "Resident deleted successfully."
        )

        return redirect(
            "resident_list"
        )

    # --------------------------------------------------------
    # CONFIRMATION PAGE
    # --------------------------------------------------------

    return render(
        request,
        "residentmodule/resident_confirm_delete.html",
        {
            "resident":
                resident
        }
    )