from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.db import transaction

from .models import User, Resident

import os
import random
import uuid

# =====================================================
# HELPER - GET REGISTRATION SESSION DATA
# =====================================================

def get_registration_data(request):
    """
    Get the current registration information stored
    inside the Django session.
    """

    return request.session.get(
        "registration_data",
        {}
    )


# =====================================================
# HELPER - SAVE REGISTRATION SESSION DATA
# =====================================================

def save_registration_data(request, registration_data):
    """
    Save registration information into the session.
    """

    request.session["registration_data"] = registration_data

    request.session.modified = True


# =====================================================
# STEP 1 — PERSONAL INFORMATION
# =====================================================

def registration(request):

    registration_data = get_registration_data(request)

    if request.method == "POST":

        # -------------------------------------------------
        # GET FORM DATA
        # -------------------------------------------------

        full_name = request.POST.get(
            "full_name",
            ""
        ).strip()

        birth_date = request.POST.get(
            "birth_date",
            ""
        ).strip()

        gender = request.POST.get(
            "gender",
            ""
        ).strip()

        civil_status = request.POST.get(
            "civil_status",
            ""
        ).strip()

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        profile_picture = request.FILES.get(
            "profile_picture"
        )


        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        if not all([
            full_name,
            birth_date,
            gender,
            civil_status,
            username,
        ]):

            return render(
                request,
                "registration/registration.html",
                {
                    "error":
                        "Please complete all required fields.",

                    "registration_data":
                        registration_data,

                    "full_name":
                        full_name,

                    "birth_date":
                        birth_date,

                    "gender":
                        gender,

                    "civil_status":
                        civil_status,

                    "username":
                        username,
                }
            )


        # -------------------------------------------------
        # USERNAME VALIDATION
        # -------------------------------------------------

        existing_username = (
            registration_data.get(
                "username",
                ""
            )
        )

        username_query = User.objects.filter(
            username=username
        )

        if (
            existing_username
            and existing_username == username
        ):

            username_query = (
                username_query.exclude(
                    username=existing_username
                )
            )

        if username_query.exists():

            return render(
                request,
                "registration/registration.html",
                {
                    "error":
                        "That username is already in use.",

                    "registration_data":
                        registration_data,

                    "full_name":
                        full_name,

                    "birth_date":
                        birth_date,

                    "gender":
                        gender,

                    "civil_status":
                        civil_status,

                    "username":
                        username,
                }
            )


        # -------------------------------------------------
        # PASSWORD VALIDATION
        # -------------------------------------------------

        existing_password = (
            registration_data.get(
                "password",
                ""
            )
        )

        # If the applicant returned from Step 2,
        # allow the previously entered password
        # to remain in the registration session.

        if (
            not password
            and existing_password
        ):

            password = existing_password
            confirm_password = existing_password

        else:

            if not password:

                return render(
                    request,
                    "registration/registration.html",
                    {
                        "error":
                            "Please enter a password.",

                        "registration_data":
                            registration_data,

                        "full_name":
                            full_name,

                        "birth_date":
                            birth_date,

                        "gender":
                            gender,

                        "civil_status":
                            civil_status,

                        "username":
                            username,
                    }
                )


            if len(password) < 8:

                return render(
                    request,
                    "registration/registration.html",
                    {
                        "error":
                            "Password must be at least 8 characters long.",

                        "registration_data":
                            registration_data,

                        "full_name":
                            full_name,

                        "birth_date":
                            birth_date,

                        "gender":
                            gender,

                        "civil_status":
                            civil_status,

                        "username":
                            username,
                    }
                )


            if password != confirm_password:

                return render(
                    request,
                    "registration/registration.html",
                    {
                        "error":
                            "Passwords do not match.",

                        "registration_data":
                            registration_data,

                        "full_name":
                            full_name,

                        "birth_date":
                            birth_date,

                        "gender":
                            gender,

                        "civil_status":
                            civil_status,

                        "username":
                            username,
                    }
                )


        # -------------------------------------------------
        # PROFILE PICTURE REQUIRED
        # -------------------------------------------------

        existing_profile_picture = (
            registration_data.get(
                "profile_picture_path"
            )
        )

        if (
            not profile_picture
            and not existing_profile_picture
        ):

            return render(
                request,
                "registration/registration.html",
                {
                    "error":
                        "Please upload your profile picture.",

                    "registration_data":
                        registration_data,

                    "full_name":
                        full_name,

                    "birth_date":
                        birth_date,

                    "gender":
                        gender,

                    "civil_status":
                        civil_status,

                    "username":
                        username,
                }
            )


        # -------------------------------------------------
        # PROFILE PICTURE VALIDATION
        # -------------------------------------------------

        if profile_picture:

            max_profile_size = (
                5 * 1024 * 1024
            )

            if (
                profile_picture.size
                > max_profile_size
            ):

                return render(
                    request,
                    "registration/registration.html",
                    {
                        "error":
                            "Profile picture must not exceed 5 MB.",

                        "registration_data":
                            registration_data,

                        "full_name":
                            full_name,

                        "birth_date":
                            birth_date,

                        "gender":
                            gender,

                        "civil_status":
                            civil_status,

                        "username":
                            username,
                    }
                )


            extension = os.path.splitext(
                profile_picture.name
            )[1].lower()


            allowed_profile_extensions = [
                ".jpg",
                ".jpeg",
                ".png",
            ]


            if (
                extension
                not in allowed_profile_extensions
            ):

                return render(
                    request,
                    "registration/registration.html",
                    {
                        "error":
                            "Profile picture must be JPG, JPEG, or PNG.",

                        "registration_data":
                            registration_data,

                        "full_name":
                            full_name,

                        "birth_date":
                            birth_date,

                        "gender":
                            gender,

                        "civil_status":
                            civil_status,

                        "username":
                            username,
                    }
                )


        # -------------------------------------------------
        # SAVE PROFILE PICTURE
        # -------------------------------------------------

        if profile_picture:

            old_profile_picture = (
                registration_data.get(
                    "profile_picture_path"
                )
            )


            # Delete the previous temporary profile
            # picture if the applicant selected
            # another one.

            if (
                old_profile_picture
                and default_storage.exists(
                    old_profile_picture
                )
            ):

                default_storage.delete(
                    old_profile_picture
                )


            extension = os.path.splitext(
                profile_picture.name
            )[1].lower()


            unique_filename = (
                f"{uuid.uuid4().hex}"
                f"{extension}"
            )


            profile_picture_path = (
                default_storage.save(
                    os.path.join(
                        "resident_profiles",
                        unique_filename
                    ),
                    profile_picture
                )
            )


            registration_data[
                "profile_picture_path"
            ] = profile_picture_path

            registration_data[
                "profile_picture_name"
            ] = profile_picture.name


        # -------------------------------------------------
        # SAVE STEP 1 DATA
        # -------------------------------------------------

        registration_data.update({

            "full_name":
                full_name,

            "birth_date":
                birth_date,

            "gender":
                gender,

            "civil_status":
                civil_status,

            "username":
                username,

            "password":
                password,

        })


        save_registration_data(
            request,
            registration_data
        )


        # -------------------------------------------------
        # NEXT STEP
        # -------------------------------------------------

        return redirect(
            "step2_contact"
        )


    # =====================================================
    # GET REQUEST
    # =====================================================

    return render(
        request,
        "registration/registration.html",
        {
            "registration_data":
                registration_data,

            "full_name":
                registration_data.get(
                    "full_name",
                    ""
                ),

            "birth_date":
                registration_data.get(
                    "birth_date",
                    ""
                ),

            "gender":
                registration_data.get(
                    "gender",
                    ""
                ),

            "civil_status":
                registration_data.get(
                    "civil_status",
                    ""
                ),

            "username":
                registration_data.get(
                    "username",
                    ""
                ),
        }
    )


# =====================================================
# STEP 2 — CONTACT & ADDRESS
# =====================================================

def step2_contact(request):

    registration_data = get_registration_data(
        request
    )

    # -------------------------------------------------
    # PREVENT DIRECT ACCESS
    # -------------------------------------------------

    if not registration_data:

        return redirect(
            "registration"
        )

    # -------------------------------------------------
    # POST STEP 2
    # -------------------------------------------------

    if request.method == "POST":

        # -------------------------------------------------
        # GET BUTTON ACTION
        #
        # back = save and return to Step 1
        # next = save and continue to Step 3
        # -------------------------------------------------

        action = request.POST.get(
            "action",
            "next"
        )

        # -------------------------------------------------
        # GET STEP 2 VALUES
        # -------------------------------------------------

        mobile_number = request.POST.get(
            "mobile_number",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        house_block_lot = request.POST.get(
            "house_block_lot",
            ""
        ).strip()

        street = request.POST.get(
            "street",
            ""
        ).strip()

        province = request.POST.get(
            "province",
            ""
        ).strip()

        municipality = request.POST.get(
            "municipality",
            ""
        ).strip()

        barangay = request.POST.get(
            "barangay",
            ""
        ).strip()

        zip_code = request.POST.get(
            "zip_code",
            ""
        ).strip()

        # -------------------------------------------------
        # SAVE STEP 2 BEFORE ANY REDIRECT
        #
        # This is what prevents information from
        # disappearing when clicking Back.
        # -------------------------------------------------

        registration_data.update({

            "mobile_number":
                mobile_number,

            "email":
                email,

            "house_block_lot":
                house_block_lot,

            "street":
                street,

            "province":
                province,

            "municipality":
                municipality,

            "barangay":
                barangay,

            "zip_code":
                zip_code,

        })

        save_registration_data(
            request,
            registration_data
        )

        # -------------------------------------------------
        # BACK → STEP 1
        #
        # No validation is required when going backward.
        # The entered Step 2 data has already been saved.
        # -------------------------------------------------

        if action == "back":

            return redirect(
                "registration"
            )

        # -------------------------------------------------
        # VALIDATE STEP 2 WHEN GOING FORWARD
        # -------------------------------------------------

        if not mobile_number:

            return render(
                request,
                "registration/step2_contact.html",
                {
                    "registration_data":
                        registration_data,

                    "error":
                        "Please enter your mobile number."
                }
            )

        if not email:

            return render(
                request,
                "registration/step2_contact.html",
                {
                    "registration_data":
                        registration_data,

                    "error":
                        "Please enter your email address."
                }
            )

        if not province:

            return render(
                request,
                "registration/step2_contact.html",
                {
                    "registration_data":
                        registration_data,

                    "error":
                        "Please select your province."
                }
            )

        if not municipality:

            return render(
                request,
                "registration/step2_contact.html",
                {
                    "registration_data":
                        registration_data,

                    "error":
                        "Please select your municipality or city."
                }
            )

        if not barangay:

            return render(
                request,
                "registration/step2_contact.html",
                {
                    "registration_data":
                        registration_data,

                    "error":
                        "Please select your barangay."
                }
            )

        # -------------------------------------------------
        # STEP 2 → STEP 3
        # -------------------------------------------------

        return redirect(
            "step3_identity"
        )

    # -------------------------------------------------
    # DISPLAY STEP 2
    #
    # Values come from registration_data, so they
    # reappear after returning from another page.
    # -------------------------------------------------

    return render(
        request,
        "registration/step2_contact.html",
        {
            "registration_data":
                registration_data
        }
    )


# =====================================================
# STEP 3 — IDENTITY & RESIDENCY VERIFICATION
# =====================================================

def step3_identity(request):

    registration_data = get_registration_data(
        request
    )

    # -------------------------------------------------
    # PREVENT DIRECT ACCESS
    # -------------------------------------------------

    if not registration_data:

        return redirect(
            "registration"
        )

    # -------------------------------------------------
    # POST STEP 3
    # -------------------------------------------------

    if request.method == "POST":

        action = request.POST.get(
            "action",
            "next"
        )

        # -------------------------------------------------
        # BACK TO STEP 2
        # -------------------------------------------------

        if action == "back":

            return redirect(
                "step2_contact"
            )

        id_type = request.POST.get(
            "id_type",
            ""
        ).strip()

        id_number = request.POST.get(
            "id_number",
            ""
        ).strip()

        document_type = request.POST.get(
            "document_type",
            ""
        ).strip()

        valid_id = request.FILES.get(
            "valid_id"
        )

        residency_proof = request.FILES.get(
            "residency_proof"
        )

        # -------------------------------------------------
        # VALIDATE REQUIRED FIELDS
        # -------------------------------------------------

        if not id_type:

            return render(
                request,
                "registration/step3_identity.html",
                {
                    "registration_data":
                        registration_data,

                    "error":
                        "Please select an ID type."
                }
            )

        if not id_number:

            return render(
                request,
                "registration/step3_identity.html",
                {
                    "registration_data":
                        registration_data,

                    "error":
                        "Please enter your ID number."
                }
            )

        if not document_type:

            return render(
                request,
                "registration/step3_identity.html",
                {
                    "registration_data":
                        registration_data,

                    "error":
                        "Please select a residency document type."
                }
            )

        # -------------------------------------------------
        # EXISTING FILES
        #
        # If Step 3 was previously completed and the user
        # came back, existing saved files can be reused.
        # -------------------------------------------------

        existing_valid_id = registration_data.get(
            "valid_id"
        )

        existing_residency_proof = registration_data.get(
            "residency_proof"
        )

        if not valid_id and not existing_valid_id:

            return render(
                request,
                "registration/step3_identity.html",
                {
                    "registration_data":
                        registration_data,

                    "error":
                        "Please upload your valid government ID."
                }
            )

        if (
            not residency_proof
            and not existing_residency_proof
        ):

            return render(
                request,
                "registration/step3_identity.html",
                {
                    "registration_data":
                        registration_data,

                    "error":
                        "Please upload your proof of residency."
                }
            )

        # -------------------------------------------------
        # MAXIMUM FILE SIZE = 5 MB
        # -------------------------------------------------

        max_file_size = (
            5 * 1024 * 1024
        )

        if (
            valid_id
            and valid_id.size > max_file_size
        ):

            return render(
                request,
                "registration/step3_identity.html",
                {
                    "registration_data":
                        registration_data,

                    "error":
                        "Government ID must not exceed 5MB."
                }
            )

        if (
            residency_proof
            and residency_proof.size > max_file_size
        ):

            return render(
                request,
                "registration/step3_identity.html",
                {
                    "registration_data":
                        registration_data,

                    "error":
                        "Proof of residency must not exceed 5MB."
                }
            )

        # -------------------------------------------------
        # ALLOWED FILE TYPES
        # -------------------------------------------------

        allowed_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".pdf",
        ]

        if valid_id:

            valid_id_extension = os.path.splitext(
                valid_id.name
            )[1].lower()

            if (
                valid_id_extension
                not in allowed_extensions
            ):

                return render(
                    request,
                    "registration/step3_identity.html",
                    {
                        "registration_data":
                            registration_data,

                        "error":
                            "Invalid Government ID file type. "
                            "Only JPG, JPEG, PNG, and PDF are allowed."
                    }
                )

        if residency_proof:

            residency_extension = os.path.splitext(
                residency_proof.name
            )[1].lower()

            if (
                residency_extension
                not in allowed_extensions
            ):

                return render(
                    request,
                    "registration/step3_identity.html",
                    {
                        "registration_data":
                            registration_data,

                        "error":
                            "Invalid residency document file type. "
                            "Only JPG, JPEG, PNG, and PDF are allowed."
                    }
                )

        # -------------------------------------------------
        # SAVE NEW GOVERNMENT ID
        # -------------------------------------------------

        if valid_id:

            valid_id_path = default_storage.save(
                os.path.join(
                    "registration_documents",
                    valid_id.name
                ),
                ContentFile(
                    valid_id.read()
                )
            )

            registration_data[
                "valid_id"
            ] = valid_id_path

            registration_data[
                "valid_id_name"
            ] = valid_id.name

        # -------------------------------------------------
        # SAVE NEW RESIDENCY PROOF
        # -------------------------------------------------

        if residency_proof:

            residency_path = default_storage.save(
                os.path.join(
                    "registration_documents",
                    residency_proof.name
                ),
                ContentFile(
                    residency_proof.read()
                )
            )

            registration_data[
                "residency_proof"
            ] = residency_path

            registration_data[
                "residency_proof_name"
            ] = residency_proof.name

        # -------------------------------------------------
        # SAVE STEP 3 TEXT DATA
        # -------------------------------------------------

        registration_data.update({

            "id_type":
                id_type,

            "id_number":
                id_number,

            "document_type":
                document_type,

        })

        save_registration_data(
            request,
            registration_data
        )

        # -------------------------------------------------
        # STEP 3 → STEP 4
        # -------------------------------------------------

        return redirect(
            "step4_review"
        )

    # -------------------------------------------------
    # DISPLAY STEP 3
    # -------------------------------------------------

    return render(
        request,
        "registration/step3_identity.html",
        {
            "registration_data":
                registration_data
        }
    )


# =====================================================
# STEP 4 — REVIEW & FINAL SUBMISSION
# =====================================================

def step4_review(request):

    registration_data = get_registration_data(
        request
    )

    # -------------------------------------------------
    # PREVENT DIRECT ACCESS
    # -------------------------------------------------

    if not registration_data:

        return redirect(
            "registration"
        )

    # -------------------------------------------------
    # POST STEP 4
    # -------------------------------------------------

    if request.method == "POST":

        action = request.POST.get(
            "action",
            "submit"
        )

        # -------------------------------------------------
        # BACK → STEP 3
        # -------------------------------------------------

        if action == "back":

            return redirect(
                "step3_identity"
            )

        # -------------------------------------------------
        # CHECK DECLARATION
        # -------------------------------------------------

        if not request.POST.get(
            "truth_declaration"
        ):

            return render(
                request,
                "registration/step4_review.html",
                {
                    "registration_data":
                        registration_data,

                    "error":
                        "Please confirm that the information "
                        "you provided is true and complete."
                }
            )

        # -------------------------------------------------
        # CHECK DATA CONSENT
        # -------------------------------------------------

        if not request.POST.get(
            "data_consent"
        ):

            return render(
                request,
                "registration/step4_review.html",
                {
                    "registration_data":
                        registration_data,

                    "error":
                        "Please agree to the collection and "
                        "processing of your information."
                }
            )

        # -------------------------------------------------
        # CHECK USERNAME
        # -------------------------------------------------

        username = registration_data.get(
            "username",
            ""
        )

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "registration/step4_review.html",
                {
                    "registration_data":
                        registration_data,

                    "error":
                        "Username already exists."
                }
            )

        # -------------------------------------------------
        # EMAIL
        # -------------------------------------------------

        email = registration_data.get(
            "email",
            ""
        )

        # -------------------------------------------------
        # SPLIT FULL NAME
        # -------------------------------------------------

        full_name = registration_data.get(
            "full_name",
            ""
        ).strip()

        name_parts = full_name.split()

        first_name = (
            name_parts[0]
            if len(name_parts) >= 1
            else ""
        )

        last_name = (
            name_parts[-1]
            if len(name_parts) >= 2
            else ""
        )

        middle_name = (
            " ".join(
                name_parts[1:-1]
            )
            if len(name_parts) >= 3
            else None
        )

        # -------------------------------------------------
        # GENERATE UNIQUE APPLICATION REFERENCE
        # -------------------------------------------------

        year = timezone.now().year

        random_number = random.randint(
            100000,
            999999
        )

        application_reference = (
            f"BB-{year}-{random_number}"
        )

        # -------------------------------------------------
        # BUILD CLEAN ADDRESS
        # -------------------------------------------------

        address_parts = [

            registration_data.get(
                "house_block_lot",
                ""
            ),

            registration_data.get(
                "street",
                ""
            ),

            registration_data.get(
                "barangay",
                ""
            ),

            registration_data.get(
                "municipality",
                ""
            ),

            registration_data.get(
                "province",
                ""
            ),

            registration_data.get(
                "zip_code",
                ""
            ),

        ]

        address = ", ".join(
            part
            for part in address_parts
            if part
        )

        # -------------------------------------------------
        # SAVE USER + RESIDENT
        # -------------------------------------------------

        try:

            with transaction.atomic():

                # -----------------------------------------
                # CREATE USER
                # -----------------------------------------

                user = User.objects.create(

                    username=
                        username,

                    password_hash=
                        make_password(
                            registration_data[
                                "password"
                            ]
                        ),

                    email=
                        email,

                    role=
                        "Resident",

                    is_active=
                        True,

                )

                # -----------------------------------------
                # CREATE RESIDENT
                # -----------------------------------------

                Resident.objects.create(

                    user_id=
                        user.user_id,

                    first_name=
                        first_name,

                    middle_name=
                        middle_name,

                    last_name=
                        last_name,

                    birth_date=
                        registration_data.get(
                            "birth_date"
                        ),

                    gender=
                        registration_data.get(
                            "gender"
                        ),

                    civil_status=
                        registration_data.get(
                            "civil_status"
                        ),

                    address=
                        address,

                    contact_number=
                        registration_data.get(
                            "mobile_number"
                        ),

                    house_block_lot=
                        registration_data.get(
                            "house_block_lot"
                        ),

                    street_purok_sitio=
                        registration_data.get(
                            "street"
                        ),

                    province=
                        registration_data.get(
                            "province"
                        ),

                    municipality_city=
                        registration_data.get(
                            "municipality"
                        ),

                    barangay=
                        registration_data.get(
                            "barangay"
                        ),

                    zip_code=
                        registration_data.get(
                            "zip_code"
                        ),

                    email=
                        email,
                        
                    profile_picture_path=registration_data.get(
                        "profile_picture_path"
                    ),

                    # =============================================
                    # GOVERNMENT-ISSUED ID
                    # =============================================

                    id_type=
                        registration_data.get(
                            "id_type"
                        ),

                    id_number=
                        registration_data.get(
                            "id_number"
                        ),

                    id_file_path=
                        registration_data.get(
                            "valid_id"
                        ),

                    # =============================================
                    # PROOF OF RESIDENCY
                    # =============================================

                    residency_document_type=
                        registration_data.get(
                            "document_type"
                        ),

                    residency_file_path=
                        registration_data.get(
                            "residency_proof"
                        ),

                    # =============================================
                    # VERIFICATION
                    # =============================================

                    verification_status=
                        "Pending",

                )

        except Exception as e:

            return render(
                request,
                "registration/step4_review.html",
                {
                    "registration_data":
                        registration_data,

                    "error":
                        f"Registration failed: {str(e)}"
                }
            )

        # -------------------------------------------------
        # SAVE APPLICATION INFORMATION
        # -------------------------------------------------

        registration_data[
            "application_reference"
        ] = application_reference

        registration_data[
            "submitted_date"
        ] = timezone.now().strftime(
            "%B %d, %Y"
        )

        registration_data[
            "status"
        ] = "Pending Verification"

        save_registration_data(
            request,
            registration_data
        )

        # -------------------------------------------------
        # GO TO SUCCESS PAGE
        # -------------------------------------------------

        return redirect(
            "registration_success"
        )

    # -------------------------------------------------
    # DISPLAY STEP 4
    # -------------------------------------------------

    return render(
        request,
        "registration/step4_review.html",
        {
            "registration_data":
                registration_data
        }
    )


# =====================================================
# REGISTRATION SUCCESS
# =====================================================

def registration_success(request):

    registration_data = get_registration_data(
        request
    )

    if not registration_data:

        return redirect(
            "registration"
        )

    return render(
        request,
        "registration/registration_success.html",
        {

            "registration_data":
                registration_data,

            "application_reference":
                registration_data.get(
                    "application_reference",
                    ""
                ),

            "submitted_date":
                registration_data.get(
                    "submitted_date",
                    timezone.now().strftime(
                        "%B %d, %Y"
                    )
                ),

            "status":
                registration_data.get(
                    "status",
                    "Pending Verification"
                ),

        }
    )