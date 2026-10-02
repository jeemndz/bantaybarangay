from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from bantaybarangay.security import role_required

from .models import Resident
from .forms import ResidentForm
from django.conf import settings

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
        "residents":
            residents,

        "verification_residents":
            verification_residents,

        "total_residents":
            residents.count(),

        # You can calculate these later
        # from your actual resident data.
        "total_households":
            0,

        "senior_citizens":
            0,

        "pwd_residents":
            0,
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
    # GOVERNMENT ID URL
    # --------------------------------------------------------

    id_file_url = None
    id_file_is_image = False
    id_file_is_pdf = False

    if resident.id_file_path:

        clean_id_path = (
            str(resident.id_file_path)
            .replace("\\", "/")
            .lstrip("/")
        )

        id_file_url = (
            f"{settings.MEDIA_URL}"
            f"{clean_id_path}"
        )

        lower_id_path = clean_id_path.lower()

        id_file_is_image = lower_id_path.endswith(
            (
                ".jpg",
                ".jpeg",
                ".png",
            )
        )

        id_file_is_pdf = lower_id_path.endswith(
            ".pdf"
        )

    # --------------------------------------------------------
    # RESIDENCY DOCUMENT URL
    # --------------------------------------------------------

    residency_file_url = None
    residency_file_is_image = False
    residency_file_is_pdf = False

    if resident.residency_file_path:

        clean_residency_path = (
            str(resident.residency_file_path)
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

    context = {
        "resident":
            resident,

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

    if request.method == "POST":

        resident.verification_status = (
            "Verified"
        )

        resident.verified_at = (
            timezone.now()
        )

        # Save the logged-in admin/official
        # who verified this resident.
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

        return redirect(
            "resident_list"
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

    if request.method == "POST":

        resident.verification_status = (
            "Rejected"
        )

        resident.verified_at = (
            timezone.now()
        )

        # Save the logged-in admin/official
        # who rejected this resident.
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

        return redirect(
            "resident_list"
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