import hashlib
import os
import uuid

from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.core.files.storage import default_storage
from django.db import connection, transaction
from django.shortcuts import render, redirect


# =====================================================
# EVIDENCE CONFIGURATION
# =====================================================

MAX_EVIDENCE_FILES = 5

MAX_EVIDENCE_FILE_SIZE = (
    10 * 1024 * 1024
)  # 10 MB


ALLOWED_EVIDENCE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",

    ".mp4",
    ".webm",
    ".mov",

    ".pdf",
    ".doc",
    ".docx",
}


# =====================================================
# HELPER: SESSION CONTEXT
# =====================================================

def get_session_context(request):
    """
    Return the common session information used by
    the website templates.
    """

    return {
        "user_id": request.session.get(
            "user_id"
        ),

        "username": request.session.get(
            "username",
            ""
        ),

        "email": request.session.get(
            "email",
            ""
        ),

        "role": request.session.get(
            "role",
            ""
        ),
    }


# =====================================================
# HELPER: GET RESIDENT
# =====================================================

def get_resident_by_user_id(user_id):
    """
    Get the resident record connected to the
    currently logged-in user.
    """

    if not user_id:
        return None

    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                resident_id,
                first_name,
                middle_name,
                last_name,
                suffix,
                email,
                contact_number,
                address,
                verification_status
            FROM residents
            WHERE user_id = %s
            LIMIT 1
            """,
            [
                user_id
            ]
        )

        row = cursor.fetchone()

    if not row:
        return None

    return {
        "resident_id":
            row[0],

        "first_name":
            row[1],

        "middle_name":
            row[2],

        "last_name":
            row[3],

        "suffix":
            row[4],

        "email":
            row[5],

        "contact_number":
            row[6],

        "address":
            row[7],

        "verification_status":
            row[8],
    }


# =====================================================
# HELPER: BUILD RESIDENT FULL NAME
# =====================================================

def build_resident_full_name(resident):
    """
    Build a resident's full name while safely
    ignoring empty name fields.
    """

    if not resident:
        return ""

    name_parts = [
        resident.get(
            "first_name"
        ),

        resident.get(
            "middle_name"
        ),

        resident.get(
            "last_name"
        ),

        resident.get(
            "suffix"
        ),
    ]

    return " ".join(
        str(part).strip()

        for part in name_parts

        if part and str(part).strip()
    )


# =====================================================
# HELPER: PREPARE RESIDENT PROFILE
# =====================================================

def prepare_resident_profile(resident):
    """
    Add template-friendly values to the resident
    dictionary without requiring duplicate columns
    in the database.
    """

    if not resident:
        return None

    # Work with a copy so other views do not
    # unexpectedly modify the original dictionary.
    resident = resident.copy()

    full_name = build_resident_full_name(
        resident
    )

    resident["full_name"] = (
        full_name
    )

    resident["mobile_number"] = (
        resident.get(
            "contact_number"
        )
        or ""
    )

    resident["address_line"] = (
        resident.get(
            "address"
        )
        or ""
    )

    resident["full_address"] = (
        resident.get(
            "address"
        )
        or ""
    )

    # =================================================
    # DISPLAY RESIDENT NUMBER
    # =================================================

    resident_id = resident.get(
        "resident_id"
    )

    if resident_id:

        try:

            resident["resident_number"] = (
                f"BB-RES-{int(resident_id):06d}"
            )

        except (
            TypeError,
            ValueError
        ):

            resident["resident_number"] = (
                f"BB-RES-{resident_id}"
            )

    else:

        resident["resident_number"] = ""


    # =================================================
    # VERIFICATION
    # =================================================

    verification_status = (
        resident.get(
            "verification_status"
        )
        or ""
    )

    resident["is_verified"] = (
        str(
            verification_status
        )
        .strip()
        .lower()
        in {
            "verified",
            "approved",
        }
    )


    # =================================================
    # OPTIONAL PROFILE FIELDS
    # =================================================
    #
    # These values are currently not returned by the
    # residents query above. They are provided so the
    # profile template can safely display empty values.
    #
    # Once these columns exist in the database, add them
    # to get_resident_by_user_id().
    # =================================================

    resident.setdefault(
        "profile_picture",
        None
    )

    resident.setdefault(
        "birth_date",
        None
    )

    resident.setdefault(
        "age",
        None
    )

    resident.setdefault(
        "gender",
        ""
    )

    resident.setdefault(
        "civil_status",
        ""
    )

    resident.setdefault(
        "registration_date",
        None
    )

    resident.setdefault(
        "barangay",
        ""
    )

    resident.setdefault(
        "zone",
        ""
    )

    resident.setdefault(
        "geo_id",
        ""
    )

    resident.setdefault(
        "household_head",
        ""
    )

    resident.setdefault(
        "family_count",
        ""
    )

    resident.setdefault(
        "identity_hash",
        ""
    )

    return resident


# =====================================================
# HELPER: COMPLAINT REFERENCE NUMBER
# =====================================================

def build_complaint_reference(
    complaint_id,
    submitted_at=None
):
    """
    Generate the display reference number.

    Example:

    CMP-2026-0001
    """

    if submitted_at:
        year = submitted_at.year

    else:
        year = datetime.now().year

    return (
        f"CMP-{year}-"
        f"{complaint_id:04d}"
    )


# =====================================================
# HELPER: COMPLAINT STATUS GROUP
# =====================================================

def get_complaint_status_group(status):

    if status in [
        "Submitted",
        "Under Review",
        "Under Investigation",
    ]:
        return "progress"

    if status in [
        "Resolved",
        "Closed",
    ]:
        return "resolved"

    if status == "Rejected":
        return "rejected"

    return "progress"


# =====================================================
# HELPER: COMPLAINT STATUS MESSAGE
# =====================================================

def get_complaint_status_message(
    status,
    resolution=None
):

    if resolution:
        return resolution

    status_messages = {

        "Submitted":
            "Your complaint has been submitted "
            "and is awaiting review.",

        "Under Review":
            "Your complaint is currently being "
            "reviewed by the barangay.",

        "Under Investigation":
            "Barangay officials are currently "
            "investigating this complaint.",

        "Resolved":
            "This complaint has been resolved.",

        "Rejected":
            "This complaint has been rejected. "
            "Contact the barangay for more "
            "information.",

        "Closed":
            "This complaint has been officially "
            "closed.",
    }

    return status_messages.get(
        status,
        "Your complaint is currently being processed."
    )


# =====================================================
# HELPER: VALIDATE EVIDENCE FILES
# =====================================================

def validate_evidence_files(
    evidence_files
):
    """
    Validate all evidence uploaded together with
    the complaint.

    Maximum:
        5 files

    Maximum size:
        10 MB per file
    """

    if len(evidence_files) > MAX_EVIDENCE_FILES:

        return (
            "Please select a maximum of "
            "5 evidence files."
        )

    for uploaded_file in evidence_files:

        # =============================================
        # VALIDATE FILE SIZE
        # =============================================

        if (
            uploaded_file.size >
            MAX_EVIDENCE_FILE_SIZE
        ):

            return (
                f"{uploaded_file.name} exceeds "
                "the 10MB file size limit."
            )

        # =============================================
        # VALIDATE EXTENSION
        # =============================================

        extension = (
            os.path.splitext(
                uploaded_file.name
            )[1]
            .lower()
        )

        if (
            extension not in
            ALLOWED_EVIDENCE_EXTENSIONS
        ):

            return (
                f"{uploaded_file.name} has an "
                "unsupported file type."
            )

    return None


# =====================================================
# HELPER: CALCULATE FILE HASH
# =====================================================

def calculate_file_hash(
    uploaded_file
):
    """
    Generate SHA-256 hash for uploaded evidence.
    """

    sha256 = hashlib.sha256()

    for chunk in uploaded_file.chunks():

        sha256.update(
            chunk
        )

    # Reset the uploaded file pointer so Django
    # can save the file afterward.

    try:

        uploaded_file.seek(0)

    except Exception:

        pass

    return sha256.hexdigest()


# =====================================================
# HELPER: BUILD SAFE EVIDENCE FILE NAME
# =====================================================

def build_evidence_file_name(
    uploaded_file
):
    """
    Generate a unique storage filename.

    The original filename is still stored in the
    database as file_name.
    """

    extension = (
        os.path.splitext(
            uploaded_file.name
        )[1]
        .lower()
    )

    unique_name = (
        uuid.uuid4().hex
    )

    return (
        f"{unique_name}"
        f"{extension}"
    )


# =====================================================
# HELPER: SAVE EVIDENCE
# =====================================================

def save_complaint_evidence(
    complaint_id,
    uploaded_by,
    evidence_files
):
    """
    Save evidence files to Django media storage and
    insert their metadata into the evidence table.

    Database relationship:

        complaints.complaint_id
                ↓
        evidence.complaint_id
    """

    saved_storage_paths = []

    try:

        for uploaded_file in evidence_files:

            # =========================================
            # ORIGINAL FILE INFORMATION
            # =========================================

            original_file_name = (
                uploaded_file.name
            )

            file_size = (
                uploaded_file.size
            )

            file_type = (
                uploaded_file.content_type
                or
                "application/octet-stream"
            )

            # =========================================
            # CALCULATE SHA-256 HASH
            # =========================================

            file_hash = (
                calculate_file_hash(
                    uploaded_file
                )
            )

            # =========================================
            # UNIQUE PHYSICAL FILE NAME
            # =========================================

            stored_file_name = (
                build_evidence_file_name(
                    uploaded_file
                )
            )

            # =========================================
            # STORAGE DIRECTORY
            # =========================================

            storage_path = (
                f"evidence/"
                f"complaint_{complaint_id}/"
                f"{stored_file_name}"
            )

            # =========================================
            # SAVE PHYSICAL FILE
            # =========================================

            saved_path = (
                default_storage.save(
                    storage_path,
                    uploaded_file
                )
            )

            saved_storage_paths.append(
                saved_path
            )

            # =========================================
            # FILE URL
            # =========================================

            try:

                file_path = (
                    default_storage.url(
                        saved_path
                    )
                )

            except Exception:

                file_path = (
                    f"{settings.MEDIA_URL}"
                    f"{saved_path}"
                )

            # =========================================
            # INSERT EVIDENCE INTO DATABASE
            # =========================================

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO evidence
                    (
                        complaint_id,
                        uploaded_by,
                        file_name,
                        file_path,
                        file_type,
                        file_size,
                        file_hash,
                        uploaded_at
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        NOW()
                    )
                    """,
                    [
                        complaint_id,
                        uploaded_by,
                        original_file_name,
                        file_path,
                        file_type,
                        file_size,
                        file_hash,
                    ]
                )

        return saved_storage_paths

    except Exception:

        # =============================================
        # REMOVE FILES IF DATABASE INSERT FAILS
        # =============================================

        for saved_path in saved_storage_paths:

            try:

                if default_storage.exists(
                    saved_path
                ):

                    default_storage.delete(
                        saved_path
                    )

            except Exception:

                pass

        raise


# =====================================================
# HOME
# =====================================================

def home(request):

    context = get_session_context(
        request
    )

    return render(
        request,
        "website/home.html",
        context
    )


# =====================================================
# DASHBOARD
# =====================================================

def dashboard(request):

    context = get_session_context(
        request
    )

    return render(
        request,
        "website/dashboard.html",
        context
    )


# =====================================================
# SUBMIT COMPLAINT
# =====================================================

def submit_complaint(request):

    # =================================================
    # CHECK LOGIN
    # =================================================

    user_id = request.session.get(
        "user_id"
    )

    if not user_id:

        messages.error(
            request,
            "Please log in first before "
            "submitting a complaint."
        )

        return redirect(
            "login"
        )

    # =================================================
    # GET SESSION INFORMATION
    # =================================================

    context = get_session_context(
        request
    )

    # =================================================
    # CHECK USER ROLE
    # =================================================

    role = (
        context.get(
            "role",
            ""
        )
        .strip()
        .lower()
    )

    if role != "resident":

        messages.error(
            request,
            "Only resident accounts can "
            "submit complaints."
        )

        return redirect(
            "home"
        )

    # =================================================
    # GET RESIDENT PROFILE
    # =================================================

    resident = (
        get_resident_by_user_id(
            user_id
        )
    )

    if not resident:

        messages.error(
            request,
            "Your resident profile could "
            "not be found."
        )

        return redirect(
            "home"
        )

    # =================================================
    # DEFAULT TEMPLATE CONTEXT
    # =================================================

    context.update({

        "resident":
            resident,

        "form_data":
            {},

        "complaint_submitted":
            False,

        "submitted_complaint":
            None,

        "submitted_complaint_id":
            "",

        "complaint_reference":
            "",

        "submitted_report_type":
            "",

        "submitted_complaint_type":
            "",

        "submitted_subject":
            "",

        "submitted_status":
            "",

    })

    # =================================================
    # GET REQUEST
    # =================================================

    if request.method == "GET":

        submitted_complaint = (
            request.session.pop(
                "submitted_complaint",
                None
            )
        )

        if submitted_complaint:

            context.update({

                "complaint_submitted":
                    True,

                "submitted_complaint":
                    submitted_complaint,

                "submitted_complaint_id":
                    submitted_complaint.get(
                        "complaint_id",
                        ""
                    ),

                "complaint_reference":
                    submitted_complaint.get(
                        "reference_number",
                        ""
                    ),

                "submitted_report_type":
                    submitted_complaint.get(
                        "report_type",
                        ""
                    ),

                "submitted_complaint_type":
                    submitted_complaint.get(
                        "complaint_type",
                        ""
                    ),

                "submitted_subject":
                    submitted_complaint.get(
                        "subject",
                        ""
                    ),

                "submitted_status":
                    submitted_complaint.get(
                        "status",
                        "Submitted"
                    ),

            })

        return render(
            request,
            "website/submit_complaint.html",
            context
        )

    # =================================================
    # POST REQUEST
    # =================================================

    if request.method == "POST":

        # =================================================
        # REPORT TYPE
        # =================================================

        report_type = (
            request.POST.get(
                "report_type",
                "Formal Complaint"
            )
            .strip()
        )

        # =================================================
        # RESPONDENT INFORMATION
        # =================================================

        respondent_name = (
            request.POST.get(
                "respondent_name",
                ""
            )
            .strip()
        )

        respondent_address = (
            request.POST.get(
                "respondent_address",
                ""
            )
            .strip()
        )

        respondent_relationship = (
            request.POST.get(
                "respondent_relationship",
                ""
            )
            .strip()
        )

        respondent_contact = (
            request.POST.get(
                "respondent_contact",
                ""
            )
            .strip()
        )

        # =================================================
        # COMPLAINT INFORMATION
        # =================================================

        complaint_type = (
            request.POST.get(
                "complaint_type",
                ""
            )
            .strip()
        )

        subject = (
            request.POST.get(
                "subject",
                ""
            )
            .strip()
        )

        description = (
            request.POST.get(
                "description",
                ""
            )
            .strip()
        )

        # =================================================
        # INCIDENT INFORMATION
        # =================================================

        location = (
            request.POST.get(
                "location",
                ""
            )
            .strip()
        )

        incident_date = (
            request.POST.get(
                "incident_date",
                ""
            )
            .strip()
        )

        incident_time = (
            request.POST.get(
                "incident_time",
                ""
            )
            .strip()
        )

        # =================================================
        # EVIDENCE FILES
        # =================================================

        evidence_files = (
            request.FILES.getlist(
                "evidence"
            )
        )

        # =================================================
        # PRIORITY
        # =================================================

        priority = "N/A"

        # =================================================
        # PRESERVE FORM DATA
        # =================================================

        context["form_data"] = {

            "report_type":
                report_type,

            "respondent_name":
                respondent_name,

            "respondent_address":
                respondent_address,

            "respondent_relationship":
                respondent_relationship,

            "respondent_contact":
                respondent_contact,

            "complaint_type":
                complaint_type,

            "subject":
                subject,

            "description":
                description,

            "location":
                location,

            "incident_date":
                incident_date,

            "incident_time":
                incident_time,

            "priority":
                priority,
        }

        # =================================================
        # VALIDATE REPORT TYPE
        # =================================================

        allowed_report_types = [
            "Formal Complaint",
            "Community Issue",
        ]

        if (
            report_type not in
            allowed_report_types
        ):

            messages.error(
                request,
                "Please select a valid report type."
            )

            return render(
                request,
                "website/submit_complaint.html",
                context
            )

        # =================================================
        # VALIDATE RESPONDENT
        # =================================================

        if (
            report_type ==
            "Formal Complaint"
        ):

            if not respondent_name:

                messages.error(
                    request,
                    "Please enter the respondent's "
                    "name or known alias."
                )

                return render(
                    request,
                    "website/submit_complaint.html",
                    context
                )

            if not respondent_address:

                messages.error(
                    request,
                    "Please enter the respondent's "
                    "address or known location."
                )

                return render(
                    request,
                    "website/submit_complaint.html",
                    context
                )

        else:

            respondent_name = None
            respondent_address = None
            respondent_relationship = None
            respondent_contact = None

        # =================================================
        # VALIDATE COMPLAINT CATEGORY
        # =================================================

        if not complaint_type:

            messages.error(
                request,
                "Please select a complaint category."
            )

            return render(
                request,
                "website/submit_complaint.html",
                context
            )

        # =================================================
        # VALIDATE SUBJECT
        # =================================================

        if not subject:

            messages.error(
                request,
                "Please enter a subject."
            )

            return render(
                request,
                "website/submit_complaint.html",
                context
            )

        # =================================================
        # VALIDATE DESCRIPTION
        # =================================================

        if not description:

            messages.error(
                request,
                "Please provide a description."
            )

            return render(
                request,
                "website/submit_complaint.html",
                context
            )

        # =================================================
        # VALIDATE LOCATION
        # =================================================

        if not location:

            messages.error(
                request,
                "Please enter the incident location."
            )

            return render(
                request,
                "website/submit_complaint.html",
                context
            )

        # =================================================
        # VALIDATE INCIDENT DATE
        # =================================================

        if not incident_date:

            messages.error(
                request,
                "Please enter the incident date."
            )

            return render(
                request,
                "website/submit_complaint.html",
                context
            )

        # =================================================
        # PARSE INCIDENT DATE
        # =================================================

        try:

            parsed_incident_date = (
                datetime.strptime(
                    incident_date,
                    "%Y-%m-%d"
                )
                .date()
            )

        except ValueError:

            messages.error(
                request,
                "Invalid incident date."
            )

            return render(
                request,
                "website/submit_complaint.html",
                context
            )

        # =================================================
        # VALIDATE INCIDENT TIME
        # =================================================

        if not incident_time:

            messages.error(
                request,
                "Please enter the incident time."
            )

            return render(
                request,
                "website/submit_complaint.html",
                context
            )

        # =================================================
        # PARSE INCIDENT TIME
        # =================================================

        try:

            parsed_incident_time = (
                datetime.strptime(
                    incident_time,
                    "%H:%M"
                )
                .time()
            )

        except ValueError:

            messages.error(
                request,
                "Invalid incident time."
            )

            return render(
                request,
                "website/submit_complaint.html",
                context
            )

        # =================================================
        # VALIDATE EVIDENCE
        # =================================================

        evidence_error = (
            validate_evidence_files(
                evidence_files
            )
        )

        if evidence_error:

            messages.error(
                request,
                evidence_error
            )

            return render(
                request,
                "website/submit_complaint.html",
                context
            )

        # =================================================
        # INSERT COMPLAINT + EVIDENCE
        # =================================================

        saved_evidence_paths = []

        try:

            with transaction.atomic():

                # =========================================
                # INSERT COMPLAINT
                # =========================================

                with connection.cursor() as cursor:

                    cursor.execute(
                        """
                        INSERT INTO complaints
                        (
                            resident_id,
                            report_type,

                            respondent_name,
                            respondent_address,
                            respondent_relationship,
                            respondent_contact,

                            complaint_type,
                            subject,
                            description,

                            location,
                            incident_date,
                            incident_time,

                            priority,
                            status,

                            submitted_at,
                            updated_at
                        )
                        VALUES
                        (
                            %s,
                            %s,

                            %s,
                            %s,
                            %s,
                            %s,

                            %s,
                            %s,
                            %s,

                            %s,
                            %s,
                            %s,

                            %s,
                            'Submitted',

                            NOW(),
                            NOW()
                        )
                        """,
                        [
                            resident[
                                "resident_id"
                            ],

                            report_type,

                            respondent_name,
                            respondent_address,
                            respondent_relationship,
                            respondent_contact,

                            complaint_type,
                            subject,
                            description,

                            location,
                            parsed_incident_date,
                            parsed_incident_time,

                            priority,
                        ]
                    )

                    # =====================================
                    # GET NEW COMPLAINT ID
                    # =====================================

                    complaint_id = (
                        cursor.lastrowid
                    )

                    if not complaint_id:

                        raise Exception(
                            "Unable to retrieve "
                            "new complaint ID."
                        )

                # =========================================
                # SAVE EVIDENCE
                # =========================================

                if evidence_files:

                    saved_evidence_paths = (
                        save_complaint_evidence(
                            complaint_id=
                                complaint_id,

                            uploaded_by=
                                user_id,

                            evidence_files=
                                evidence_files
                        )
                    )

                # =========================================
                # GET DATABASE SUBMISSION DATE
                # =========================================

                with connection.cursor() as cursor:

                    cursor.execute(
                        """
                        SELECT
                            submitted_at
                        FROM complaints
                        WHERE complaint_id = %s
                        LIMIT 1
                        """,
                        [
                            complaint_id
                        ]
                    )

                    submitted_row = (
                        cursor.fetchone()
                    )

                    if submitted_row:

                        submitted_at = (
                            submitted_row[0]
                        )

                    else:

                        submitted_at = None

        except Exception as e:

            # =============================================
            # DELETE PHYSICAL FILES ON FAILURE
            # =============================================

            for saved_path in saved_evidence_paths:

                try:

                    if default_storage.exists(
                        saved_path
                    ):

                        default_storage.delete(
                            saved_path
                        )

                except Exception:

                    pass

            print(
                "COMPLAINT / EVIDENCE "
                "INSERT ERROR:",
                e
            )

            messages.error(
                request,
                "Unable to submit your complaint. "
                "Please try again."
            )

            return render(
                request,
                "website/submit_complaint.html",
                context
            )

        # =================================================
        # BUILD COMPLAINT REFERENCE
        # =================================================

        complaint_reference = (
            build_complaint_reference(
                complaint_id,
                submitted_at
            )
        )

        # =================================================
        # SAVE SUCCESS INFORMATION TO SESSION
        # =================================================

        request.session[
            "submitted_complaint"
        ] = {

            "complaint_id":
                complaint_id,

            "reference_number":
                complaint_reference,

            "report_type":
                report_type,

            "complaint_type":
                complaint_type,

            "subject":
                subject,

            "status":
                "Submitted",

            "evidence_count":
                len(
                    evidence_files
                ),
        }

        request.session.modified = True

        # =================================================
        # REDIRECT BACK TO SUBMIT PAGE
        # =================================================

        return redirect(
            "submit_complaint"
        )

    # =================================================
    # FALLBACK
    # =================================================

    return render(
        request,
        "website/submit_complaint.html",
        context
    )


# =====================================================
# MY COMPLAINTS
# =====================================================

def my_complaints(request):

    # =================================================
    # CHECK LOGIN
    # =================================================

    user_id = request.session.get(
        "user_id"
    )

    if not user_id:

        messages.error(
            request,
            "Please log in to view your complaints."
        )

        return redirect(
            "login"
        )

    # =================================================
    # SESSION CONTEXT
    # =================================================

    context = get_session_context(
        request
    )

    # =================================================
    # CHECK ROLE
    # =================================================

    role = (
        context.get(
            "role",
            ""
        )
        .strip()
        .lower()
    )

    if role != "resident":

        messages.error(
            request,
            "Only resident accounts can "
            "access My Complaints."
        )

        return redirect(
            "home"
        )

    # =================================================
    # GET RESIDENT
    # =================================================

    resident = (
        get_resident_by_user_id(
            user_id
        )
    )

    if not resident:

        messages.error(
            request,
            "Your resident profile could "
            "not be found."
        )

        return redirect(
            "home"
        )

    complaints = []

    # =================================================
    # LOAD COMPLAINTS
    # =================================================

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    c.complaint_id,
                    c.resident_id,
                    c.complaint_type,
                    c.subject,
                    c.description,
                    c.location,
                    c.incident_date,
                    c.priority,
                    c.status,
                    c.assigned_official,
                    c.resolution,
                    c.submitted_at,
                    c.updated_at,
                    c.report_type,
                    c.respondent_name,
                    c.respondent_address,
                    c.respondent_relationship,
                    c.respondent_contact,
                    c.incident_time,

                    (
                        SELECT COUNT(*)
                        FROM evidence e
                        WHERE
                            e.complaint_id =
                            c.complaint_id
                    ) AS evidence_count

                FROM complaints c

                WHERE
                    c.resident_id = %s

                ORDER BY
                    c.submitted_at DESC
                """,
                [
                    resident[
                        "resident_id"
                    ]
                ]
            )

            rows = cursor.fetchall()

        # =================================================
        # CONVERT DATABASE ROWS
        # =================================================

        for row in rows:

            complaint_id = row[0]
            complaint_type = row[2]
            subject = row[3]
            description = row[4]
            location = row[5]
            incident_date = row[6]
            priority = row[7]
            status = row[8]
            assigned_official = row[9]
            resolution = row[10]
            submitted_at = row[11]
            updated_at = row[12]
            report_type = row[13]
            respondent_name = row[14]
            respondent_address = row[15]
            respondent_relationship = row[16]
            respondent_contact = row[17]
            incident_time = row[18]

            evidence_count = (
                row[19] or 0
            )

            complaint = {

                "complaint_id":
                    complaint_id,

                "resident_id":
                    row[1],

                "report_type":
                    report_type,

                "complaint_type":
                    complaint_type,

                "subject":
                    subject,

                "description":
                    description,

                "location":
                    location,

                "incident_date":
                    incident_date,

                "incident_time":
                    incident_time,

                "respondent_name":
                    respondent_name,

                "respondent_address":
                    respondent_address,

                "respondent_relationship":
                    respondent_relationship,

                "respondent_contact":
                    respondent_contact,

                "priority":
                    priority,

                "status":
                    status,

                "assigned_official":
                    assigned_official,

                "resolution":
                    resolution,

                "submitted_at":
                    submitted_at,

                "updated_at":
                    updated_at,

                "evidence_count":
                    evidence_count,

                "reference_number":
                    build_complaint_reference(
                        complaint_id,
                        submitted_at
                    ),

                "status_group":
                    get_complaint_status_group(
                        status
                    ),

                "latest_update":
                    get_complaint_status_message(
                        status,
                        resolution
                    ),
            }

            complaints.append(
                complaint
            )

    except Exception as e:

        print(
            "MY COMPLAINTS DATABASE ERROR:",
            e
        )

        messages.error(
            request,
            "Unable to load your complaints."
        )

    # =================================================
    # STATISTICS
    # =================================================

    total_complaints = len(
        complaints
    )

    active_count = sum(
        1

        for complaint in complaints

        if complaint["status"] in [
            "Submitted",
            "Under Review",
            "Under Investigation",
        ]
    )

    resolved_count = sum(
        1

        for complaint in complaints

        if complaint["status"] in [
            "Resolved",
            "Closed",
        ]
    )

    rejected_count = sum(
        1

        for complaint in complaints

        if complaint["status"] ==
        "Rejected"
    )

    # =================================================
    # COMPLAINT CATEGORIES
    # =================================================

    categories = sorted(
        {
            complaint[
                "complaint_type"
            ]

            for complaint in complaints

            if complaint[
                "complaint_type"
            ]
        }
    )

    # =================================================
    # RESIDENT FULL NAME
    # =================================================

    resident_full_name = (
        build_resident_full_name(
            resident
        )
    )

    # =================================================
    # UPDATE CONTEXT
    # =================================================

    context.update({

        "resident":
            resident,

        "resident_full_name":
            resident_full_name,

        "complaints":
            complaints,

        "categories":
            categories,

        "total_complaints":
            total_complaints,

        "active_count":
            active_count,

        "investigation_count":
            active_count,

        "resolved_count":
            resolved_count,

        "rejected_count":
            rejected_count,
    })

    # =================================================
    # RENDER MY COMPLAINTS
    # =================================================

    return render(
        request,
        "website/my_complaints.html",
        context
    )


# =====================================================
# TRACK COMPLAINT
# =====================================================

def track_complaint(request):

    context = get_session_context(
        request
    )

    return render(
        request,
        "website/track_complaint.html",
        context
    )


# =====================================================
# VERIFY DOCUMENT
# =====================================================

def verify_document(request):

    context = get_session_context(
        request
    )

    return render(
        request,
        "website/verify_document.html",
        context
    )


# =====================================================
# REQUEST DOCUMENT
# =====================================================

def request_document(request):

    # =================================================
    # CHECK LOGIN
    # =================================================

    user_id = request.session.get(
        "user_id"
    )

    if not user_id:

        messages.error(
            request,
            "Please log in first before "
            "requesting a document."
        )

        return redirect(
            "login"
        )

    # =================================================
    # SESSION CONTEXT
    # =================================================

    context = get_session_context(
        request
    )

    # =================================================
    # GET RESIDENT
    # =================================================

    resident = (
        get_resident_by_user_id(
            user_id
        )
    )

    if not resident:

        messages.error(
            request,
            "Your resident profile could "
            "not be found."
        )

        return redirect(
            "home"
        )

    context[
        "resident"
    ] = resident

    # =================================================
    # RENDER PAGE
    # =================================================

    return render(
        request,
        "website/request_document.html",
        context
    )


# =====================================================
# ABOUT
# =====================================================

def about(request):

    context = get_session_context(
        request
    )

    return render(
        request,
        "website/about.html",
        context
    )


# =====================================================
# CONTACT
# =====================================================

def contact(request):

    context = get_session_context(
        request
    )

    return render(
        request,
        "website/contact.html",
        context
    )


# =====================================================
# MY PROFILE
# =====================================================

def my_profile(request):

    # =================================================
    # CHECK LOGIN
    # =================================================

    user_id = request.session.get(
        "user_id"
    )

    if not user_id:

        messages.error(
            request,
            "Please log in to view your profile."
        )

        return redirect(
            "login"
        )

    # =================================================
    # SESSION CONTEXT
    # =================================================

    context = get_session_context(
        request
    )

    # =================================================
    # CHECK ROLE
    # =================================================

    role = (
        context.get(
            "role",
            ""
        )
        .strip()
        .lower()
    )

    if role != "resident":

        messages.error(
            request,
            "Only resident accounts can "
            "access the resident profile."
        )

        return redirect(
            "home"
        )

    # =================================================
    # GET RESIDENT
    # =================================================

    try:

        resident = (
            get_resident_by_user_id(
                user_id
            )
        )

    except Exception as e:

        print(
            "PROFILE DATABASE ERROR:",
            e
        )

        messages.error(
            request,
            "Unable to load your resident profile."
        )

        return redirect(
            "home"
        )

    if not resident:

        messages.error(
            request,
            "Your resident profile could "
            "not be found."
        )

        return redirect(
            "home"
        )

    # =================================================
    # PREPARE PROFILE DATA
    # =================================================

    resident = (
        prepare_resident_profile(
            resident
        )
    )

    # =================================================
    # UPDATE CONTACT INFORMATION
    # =================================================

    if request.method == "POST":

        mobile_number = (
            request.POST.get(
                "mobile_number",
                ""
            )
            .strip()
        )

        email = (
            request.POST.get(
                "email",
                ""
            )
            .strip()
            .lower()
        )

        # =================================================
        # VALIDATE MOBILE NUMBER
        # =================================================

        if not mobile_number:

            messages.error(
                request,
                "Please enter your mobile number."
            )

            resident[
                "mobile_number"
            ] = mobile_number

            resident[
                "contact_number"
            ] = mobile_number

            resident[
                "email"
            ] = email

            context.update({
                "resident":
                    resident,

                "resident_full_name":
                    resident[
                        "full_name"
                    ],

                "verification_status":
                    resident.get(
                        "verification_status",
                        ""
                    ),

                "is_verified":
                    resident[
                        "is_verified"
                    ],
            })

            return render(
                request,
                "website/my_profile.html",
                context
            )

        # =================================================
        # VALIDATE EMAIL
        # =================================================

        if not email:

            messages.error(
                request,
                "Please enter your email address."
            )

            resident[
                "mobile_number"
            ] = mobile_number

            resident[
                "contact_number"
            ] = mobile_number

            resident[
                "email"
            ] = email

            context.update({
                "resident":
                    resident,

                "resident_full_name":
                    resident[
                        "full_name"
                    ],

                "verification_status":
                    resident.get(
                        "verification_status",
                        ""
                    ),

                "is_verified":
                    resident[
                        "is_verified"
                    ],
            })

            return render(
                request,
                "website/my_profile.html",
                context
            )

        # =================================================
        # UPDATE DATABASE
        # =================================================

        try:

            with transaction.atomic():

                # =========================================
                # UPDATE RESIDENT RECORD
                # =========================================

                with connection.cursor() as cursor:

                    cursor.execute(
                        """
                        UPDATE residents
                        SET
                            contact_number = %s,
                            email = %s
                        WHERE
                            resident_id = %s
                            AND user_id = %s
                        """,
                        [
                            mobile_number,
                            email,
                            resident[
                                "resident_id"
                            ],
                            user_id,
                        ]
                    )

                    if cursor.rowcount == 0:

                        raise Exception(
                            "Resident profile "
                            "was not updated."
                        )

                # =========================================
                # UPDATE USER EMAIL
                # =========================================

                with connection.cursor() as cursor:

                    cursor.execute(
                        """
                        UPDATE users
                        SET
                            email = %s
                        WHERE
                            user_id = %s
                        """,
                        [
                            email,
                            user_id,
                        ]
                    )

            # =================================================
            # UPDATE SESSION EMAIL
            # =================================================

            request.session[
                "email"
            ] = email

            request.session.modified = True

            messages.success(
                request,
                "Your contact information has "
                "been updated successfully."
            )

            # =================================================
            # POST / REDIRECT / GET
            # =================================================

            return redirect(
                "my_profile"
            )

        except Exception as e:

            print(
                "PROFILE UPDATE ERROR:",
                e
            )

            messages.error(
                request,
                "Unable to update your profile. "
                "Please try again."
            )

            # Preserve the values submitted by
            # the resident.

            resident[
                "mobile_number"
            ] = mobile_number

            resident[
                "contact_number"
            ] = mobile_number

            resident[
                "email"
            ] = email

    # =================================================
    # PROFILE CONTEXT
    # =================================================

    context.update({

        "resident":
            resident,

        "resident_full_name":
            resident[
                "full_name"
            ],

        "verification_status":
            resident.get(
                "verification_status",
                ""
            ),

        "is_verified":
            resident[
                "is_verified"
            ],
    })

    # =================================================
    # RENDER PROFILE
    # =================================================

    return render(
        request,
        "website/my_profile.html",
        context
    )