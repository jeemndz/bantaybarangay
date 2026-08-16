from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.utils import timezone
import os


# =====================================================
# STEP 1 — PERSONAL INFORMATION
# =====================================================

def registration(request):

    if request.method == "POST":

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # ---------------------------------------------
        # CHECK PASSWORD
        # ---------------------------------------------

        if password != confirm_password:

            return render(
                request,
                "registration/registration.html",
                {
                    "error": "Passwords do not match.",
                    "full_name": request.POST.get("full_name"),
                    "birth_date": request.POST.get("birth_date"),
                    "gender": request.POST.get("gender"),
                    "civil_status": request.POST.get("civil_status"),
                    "username": request.POST.get("username"),
                }
            )

        # ---------------------------------------------
        # SAVE STEP 1 TO SESSION
        # ---------------------------------------------

        request.session["registration_data"] = {

            "full_name": request.POST.get("full_name"),

            "birth_date": request.POST.get("birth_date"),

            "gender": request.POST.get("gender"),

            "civil_status": request.POST.get("civil_status"),

            "username": request.POST.get("username"),

            "password": password,
        }

        request.session.modified = True

        # ---------------------------------------------
        # STEP 1 → STEP 2
        # ---------------------------------------------

        return redirect("step2_contact")

    return render(
        request,
        "registration/registration.html"
    )


# =====================================================
# STEP 2 — CONTACT & ADDRESS
# =====================================================

def step2_contact(request):

    registration_data = request.session.get(
        "registration_data",
        {}
    )

    # Prevent accessing Step 2 without Step 1
    if not registration_data:

        return redirect("registration")

    # ---------------------------------------------
    # POST STEP 2
    # ---------------------------------------------

    if request.method == "POST":

        registration_data.update({

            "mobile_number":
                request.POST.get("mobile_number"),

            "email":
                request.POST.get("email"),

            "house_block_lot":
                request.POST.get("house_block_lot"),

            "street":
                request.POST.get("street"),

            "province":
                request.POST.get("province"),

            "municipality":
                request.POST.get("municipality"),

            "barangay":
                request.POST.get("barangay"),

            "zip_code":
                request.POST.get("zip_code"),

        })

        request.session["registration_data"] = registration_data

        request.session.modified = True

        # ---------------------------------------------
        # STEP 2 → STEP 3
        # ---------------------------------------------

        return redirect("step3_identity")

    return render(
        request,
        "registration/step2_contact.html",
        {
            "registration_data": registration_data
        }
    )


# =====================================================
# STEP 3 — IDENTITY & RESIDENCY VERIFICATION
# =====================================================

def step3_identity(request):

    registration_data = request.session.get(
        "registration_data",
        {}
    )

    # ---------------------------------------------
    # PREVENT DIRECT ACCESS
    # ---------------------------------------------

    if not registration_data:

        return redirect("registration")

    # ---------------------------------------------
    # POST STEP 3
    # ---------------------------------------------

    if request.method == "POST":

        id_type = request.POST.get("id_type")
        id_number = request.POST.get("id_number")
        document_type = request.POST.get("document_type")

        valid_id = request.FILES.get("valid_id")
        residency_proof = request.FILES.get("residency_proof")

        # ---------------------------------------------
        # VALIDATE REQUIRED FIELDS
        # ---------------------------------------------

        if not id_type:

            return render(
                request,
                "registration/step3_identity.html",
                {
                    "registration_data": registration_data,
                    "error": "Please select an ID type."
                }
            )

        if not id_number:

            return render(
                request,
                "registration/step3_identity.html",
                {
                    "registration_data": registration_data,
                    "error": "Please enter your ID number."
                }
            )

        if not document_type:

            return render(
                request,
                "registration/step3_identity.html",
                {
                    "registration_data": registration_data,
                    "error": "Please select a residency document type."
                }
            )

        if not valid_id:

            return render(
                request,
                "registration/step3_identity.html",
                {
                    "registration_data": registration_data,
                    "error": "Please upload your valid government ID."
                }
            )

        if not residency_proof:

            return render(
                request,
                "registration/step3_identity.html",
                {
                    "registration_data": registration_data,
                    "error": "Please upload your proof of residency."
                }
            )

        # ---------------------------------------------
        # CHECK FILE SIZE
        # MAXIMUM = 5MB
        # ---------------------------------------------

        max_file_size = 5 * 1024 * 1024

        if valid_id.size > max_file_size:

            return render(
                request,
                "registration/step3_identity.html",
                {
                    "registration_data": registration_data,
                    "error": "Government ID must not exceed 5MB."
                }
            )

        if residency_proof.size > max_file_size:

            return render(
                request,
                "registration/step3_identity.html",
                {
                    "registration_data": registration_data,
                    "error": "Proof of residency must not exceed 5MB."
                }
            )

        # ---------------------------------------------
        # ALLOWED FILE TYPES
        # ---------------------------------------------

        allowed_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".pdf"
        ]

        valid_id_extension = os.path.splitext(
            valid_id.name
        )[1].lower()

        residency_extension = os.path.splitext(
            residency_proof.name
        )[1].lower()

        if valid_id_extension not in allowed_extensions:

            return render(
                request,
                "registration/step3_identity.html",
                {
                    "registration_data": registration_data,
                    "error": "Invalid Government ID file type."
                }
            )

        if residency_extension not in allowed_extensions:

            return render(
                request,
                "registration/step3_identity.html",
                {
                    "registration_data": registration_data,
                    "error": "Invalid residency document file type."
                }
            )

        # ---------------------------------------------
        # SAVE UPLOADED FILES
        # ---------------------------------------------

        valid_id_path = default_storage.save(
            "registration_documents/" + valid_id.name,
            ContentFile(valid_id.read())
        )

        residency_path = default_storage.save(
            "registration_documents/" + residency_proof.name,
            ContentFile(residency_proof.read())
        )

        # ---------------------------------------------
        # SAVE STEP 3 DATA TO SESSION
        # ---------------------------------------------

        registration_data.update({

            "id_type":
                id_type,

            "id_number":
                id_number,

            "valid_id":
                valid_id_path,

            "valid_id_name":
                valid_id.name,

            "document_type":
                document_type,

            "residency_proof":
                residency_path,

            "residency_proof_name":
                residency_proof.name,

        })

        request.session["registration_data"] = registration_data

        request.session.modified = True

        # ---------------------------------------------
        # STEP 3 → STEP 4
        # ---------------------------------------------

        return redirect("step4_review")

    # ---------------------------------------------
    # DISPLAY STEP 3
    # ---------------------------------------------

    return render(
        request,
        "registration/step3_identity.html",
        {
            "registration_data": registration_data
        }
    )


# =====================================================
# STEP 4 — FINAL SUBMISSION
# =====================================================

def step4_review(request):

    registration_data = request.session.get(
        "registration_data",
        {}
    )

    if not registration_data:
        return redirect("registration")


    if request.method == "POST":

        # -------------------------------------------------
        # CHECK CONSENTS
        # -------------------------------------------------

        if not request.POST.get("truth_declaration"):
            return render(
                request,
                "registration/step4_review.html",
                {
                    "registration_data": registration_data,
                    "error": "Please confirm that the information you provided is true and complete."
                }
            )


        if not request.POST.get("data_consent"):
            return render(
                request,
                "registration/step4_review.html",
                {
                    "registration_data": registration_data,
                    "error": "Please agree to the collection and processing of your information."
                }
            )


        # -------------------------------------------------
        # GENERATE APPLICATION REFERENCE
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
        # SAVE SUBMISSION DATA
        #
        # Later, this is where you can create the
        # Resident/Application database record.
        # -------------------------------------------------

        registration_data["application_reference"] = (
            application_reference
        )

        registration_data["submitted_date"] = (
            timezone.now().strftime("%B %d, %Y")
        )

        registration_data["status"] = (
            "Pending Verification"
        )


        # Save updated session

        request.session["registration_data"] = (
            registration_data
        )


        # -------------------------------------------------
        # REDIRECT TO SUCCESS PAGE
        # -------------------------------------------------

        return redirect("registration_success")


    return render(
        request,
        "registration/step4_review.html",
        {
            "registration_data": registration_data
        }
    )


# =====================================================
# REGISTRATION SUCCESS
# =====================================================

def registration_success(request):

    registration_data = request.session.get(
        "registration_data",
        {}
    )


    if not registration_data:

        return redirect("registration")


    return render(
        request,
        "registration/registration_success.html",
        {
            "application_reference":
                registration_data.get(
                    "application_reference",
                    "BB-2026-000123"
                ),

            "submitted_date":
                registration_data.get(
                    "submitted_date",
                    timezone.now().strftime("%B %d, %Y")
                ),
        }
    )