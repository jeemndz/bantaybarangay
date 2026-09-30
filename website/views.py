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
# DOCUMENT REQUEST ATTACHMENT CONFIGURATION
# =====================================================

MAX_DOCUMENT_ATTACHMENTS = 5

MAX_DOCUMENT_ATTACHMENT_SIZE = (
    10 * 1024 * 1024
)  # 10 MB

ALLOWED_DOCUMENT_ATTACHMENT_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
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
    Generate complaint display reference.

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
# HELPER: DOCUMENT REQUEST REFERENCE NUMBER
# =====================================================

def build_document_request_reference(
    request_id,
    created_at=None
):
    """
    Generate a document request reference number.

    Example:
    DOC-2026-0001
    """

    if created_at:
        year = created_at.year
    else:
        year = datetime.now().year

    return (
        f"DOC-{year}-"
        f"{request_id:04d}"
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

    if len(evidence_files) > MAX_EVIDENCE_FILES:

        return (
            "Please select a maximum of "
            "5 evidence files."
        )

    for uploaded_file in evidence_files:

        # =============================================
        # FILE SIZE
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
        # EXTENSION
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

    sha256 = hashlib.sha256()

    for chunk in uploaded_file.chunks():

        sha256.update(
            chunk
        )

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

    saved_storage_paths = []

    try:

        for uploaded_file in evidence_files:

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

            file_hash = (
                calculate_file_hash(
                    uploaded_file
                )
            )

            stored_file_name = (
                build_evidence_file_name(
                    uploaded_file
                )
            )

            storage_path = (
                f"evidence/"
                f"complaint_{complaint_id}/"
                f"{stored_file_name}"
            )

            saved_path = (
                default_storage.save(
                    storage_path,
                    uploaded_file
                )
            )

            saved_storage_paths.append(
                saved_path
            )

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
# HELPER: VALIDATE DOCUMENT ATTACHMENTS
# =====================================================

def validate_document_attachments(
    attachment_files
):

    if len(attachment_files) > MAX_DOCUMENT_ATTACHMENTS:

        return (
            "Please select a maximum of "
            "5 supporting attachments."
        )

    for uploaded_file in attachment_files:

        # =============================================
        # FILE SIZE
        # =============================================

        if (
            uploaded_file.size >
            MAX_DOCUMENT_ATTACHMENT_SIZE
        ):

            return (
                f"{uploaded_file.name} exceeds "
                "the 10MB file size limit."
            )

        # =============================================
        # FILE EXTENSION
        # =============================================

        extension = (
            os.path.splitext(
                uploaded_file.name
            )[1]
            .lower()
        )

        if (
            extension not in
            ALLOWED_DOCUMENT_ATTACHMENT_EXTENSIONS
        ):

            return (
                f"{uploaded_file.name} has an "
                "unsupported file type."
            )

    return None


# =====================================================
# HELPER: SAVE DOCUMENT REQUEST ATTACHMENTS
# =====================================================

def save_document_request_attachments(
    request_id,
    attachment_files
):

    saved_storage_paths = []

    try:

        for uploaded_file in attachment_files:

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

            extension = (
                os.path.splitext(
                    original_file_name
                )[1]
                .lower()
            )

            # =========================================
            # UNIQUE FILE NAME
            # =========================================

            stored_file_name = (
                f"{uuid.uuid4().hex}"
                f"{extension}"
            )

            # =========================================
            # STORAGE PATH
            # =========================================

            storage_path = (
                f"document_requests/"
                f"request_{request_id}/"
                f"{stored_file_name}"
            )

            # =========================================
            # SAVE FILE
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
            # GET FILE URL
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
            # SAVE DATABASE RECORD
            # =========================================

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO
                    document_request_attachments
                    (
                        request_id,
                        file_name,
                        file_path,
                        file_type,
                        file_size,
                        uploaded_at
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        NOW()
                    )
                    """,
                    [
                        request_id,
                        original_file_name,
                        file_path,
                        file_type,
                        file_size,
                    ]
                )

        return saved_storage_paths

    except Exception:

        # =============================================
        # DELETE FILES IF SOMETHING FAILED
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
    # SESSION
    # =================================================

    context = get_session_context(
        request
    )

    # =================================================
    # ROLE
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
    # RESIDENT
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
    # DEFAULT CONTEXT
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
    # GET
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
    # POST
    # =================================================

    if request.method == "POST":

        report_type = (
            request.POST.get(
                "report_type",
                "Formal Complaint"
            )
            .strip()
        )

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

        evidence_files = (
            request.FILES.getlist(
                "evidence"
            )
        )

        priority = "N/A"

        # =================================================
        # PRESERVE FORM
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
        # VALIDATION
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
        # INSERT COMPLAINT
        # =================================================

        saved_evidence_paths = []

        try:

            with transaction.atomic():

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

                    complaint_id = (
                        cursor.lastrowid
                    )

                    if not complaint_id:

                        raise Exception(
                            "Unable to retrieve "
                            "new complaint ID."
                        )

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

        complaint_reference = (
            build_complaint_reference(
                complaint_id,
                submitted_at
            )
        )

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

        return redirect(
            "submit_complaint"
        )

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
    # SESSION
    # =================================================

    context = get_session_context(
        request
    )

    # =================================================
    # ROLE
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
    # RESIDENT
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

    resident_full_name = (
        build_resident_full_name(
            resident
        )
    )

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
    # SESSION
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
            "request barangay documents."
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

    resident_id = (
        resident[
            "resident_id"
        ]
    )

    # =================================================
    # PREPARE RESIDENT
    # =================================================

    resident = (
        prepare_resident_profile(
            resident
        )
    )

    # =================================================
    # LOAD DOCUMENT TYPES
    # =================================================

    document_types = []

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    document_type_id,
                    type_name,
                    description,
                    file_path,
                    status

                FROM document_types

                WHERE
                    status = 'Active'

                ORDER BY
                    type_name ASC
                """
            )

            rows = cursor.fetchall()

        for row in rows:

            document_types.append({

                "id":
                    row[0],

                "document_type_id":
                    row[0],

                "name":
                    row[1],

                "type_name":
                    row[1],

                "description":
                    row[2] or "",

                "file_path":
                    row[3],

                "status":
                    row[4],

                "fee":
                    0,

                "processing_time":
                    "1 business day",

                "requirements":
                    "",
            })

    except Exception as e:

        print(
            "DOCUMENT TYPE LOAD ERROR:",
            e
        )

        messages.error(
            request,
            "Unable to load available "
            "document types."
        )

    # =================================================
    # DELIVERY METHODS
    # =================================================

    delivery_methods = [

        {
            "id":
                "Barangay Pickup",

            "name":
                "Barangay Pickup",

            "description":
                "Pick up your completed document "
                "at the barangay office.",

            "fee":
                0,
        },

    ]

    # =================================================
    # PAYMENT METHODS
    # =================================================

    payment_methods = [

        {
            "id":
                "Cash",

            "name":
                "Cash at Barangay",
        },

    ]

    allowed_delivery_methods = {

        item["id"]

        for item in delivery_methods
    }

    allowed_payment_methods = {

        item["id"]

        for item in payment_methods
    }

    # =================================================
    # DEFAULT FORM DATA
    # =================================================

    form_data = {

        "document_type":
            "",

        "purpose":
            "",

        "institution":
            "",

        "request_notes":
            "",

        "delivery_method":
            "",

        "payment_method":
            "",
    }

    # =================================================
    # POST
    # =================================================

    if request.method == "POST":

        # =============================================
        # FORM VALUES
        # =============================================

        document_type_id = (
            request.POST.get(
                "document_type",
                ""
            )
            .strip()
        )

        purpose = (
            request.POST.get(
                "purpose",
                ""
            )
            .strip()
        )

        institution = (
            request.POST.get(
                "institution",
                ""
            )
            .strip()
        )

        request_notes = (
            request.POST.get(
                "request_notes",
                ""
            )
            .strip()
        )

        delivery_method = (
            request.POST.get(
                "delivery_method",
                ""
            )
            .strip()
        )

        payment_method = (
            request.POST.get(
                "payment_method",
                ""
            )
            .strip()
        )

        attachment_files = (
            request.FILES.getlist(
                "attachments"
            )
        )

        # =============================================
        # PRESERVE FORM
        # =============================================

        form_data = {

            "document_type":
                document_type_id,

            "purpose":
                purpose,

            "institution":
                institution,

            "request_notes":
                request_notes,

            "delivery_method":
                delivery_method,

            "payment_method":
                payment_method,
        }

        # =============================================
        # VALIDATION
        # =============================================

        validation_error = None

        if not document_type_id:

            validation_error = (
                "Please select a document type."
            )

        elif not purpose:

            validation_error = (
                "Please enter the purpose "
                "of your request."
            )

        elif len(purpose) > 255:

            validation_error = (
                "Purpose must not exceed "
                "255 characters."
            )

        elif len(institution) > 255:

            validation_error = (
                "Institution must not exceed "
                "255 characters."
            )

        elif not delivery_method:

            validation_error = (
                "Please select a release method."
            )

        elif (
            delivery_method
            not in allowed_delivery_methods
        ):

            validation_error = (
                "Invalid release method."
            )

        elif not payment_method:

            validation_error = (
                "Please select a payment method."
            )

        elif (
            payment_method
            not in allowed_payment_methods
        ):

            validation_error = (
                "Invalid payment method."
            )

        # =============================================
        # ATTACHMENT VALIDATION
        # =============================================

        if not validation_error:

            attachment_error = (
                validate_document_attachments(
                    attachment_files
                )
            )

            if attachment_error:

                validation_error = (
                    attachment_error
                )

        # =============================================
        # PARSE DOCUMENT TYPE
        # =============================================

        parsed_document_type_id = None

        if not validation_error:

            try:

                parsed_document_type_id = int(
                    document_type_id
                )

                if (
                    parsed_document_type_id <= 0
                ):

                    raise ValueError

            except (
                TypeError,
                ValueError
            ):

                validation_error = (
                    "Invalid document type."
                )

        # =============================================
        # VERIFY DOCUMENT TYPE
        # =============================================

        selected_document = None

        if not validation_error:

            try:

                with connection.cursor() as cursor:

                    cursor.execute(
                        """
                        SELECT
                            document_type_id,
                            type_name

                        FROM document_types

                        WHERE
                            document_type_id = %s
                            AND status = 'Active'

                        LIMIT 1
                        """,
                        [
                            parsed_document_type_id
                        ]
                    )

                    selected_document = (
                        cursor.fetchone()
                    )

            except Exception as e:

                print(
                    "DOCUMENT TYPE "
                    "VALIDATION ERROR:",
                    e
                )

                validation_error = (
                    "Unable to verify the "
                    "selected document."
                )

            if (
                not validation_error
                and
                not selected_document
            ):

                validation_error = (
                    "The selected document type "
                    "is currently unavailable."
                )

        # =============================================
        # VALIDATION ERROR
        # =============================================

        if validation_error:

            messages.error(
                request,
                validation_error
            )

        else:

            # =========================================
            # SAVE REQUEST
            # =========================================

            saved_attachment_paths = []

            try:

                with transaction.atomic():

                    # =================================
                    # INSERT REQUEST
                    # =================================

                    with connection.cursor() as cursor:

                        cursor.execute(
                            """
                            INSERT INTO document_requests
                            (
                                reference_number,
                                resident_id,
                                document_type_id,
                                purpose,
                                institution,
                                request_notes,
                                delivery_method,
                                payment_method,
                                status,
                                created_at,
                                updated_at
                            )
                            VALUES
                            (
                                NULL,
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
                                resident_id,

                                parsed_document_type_id,

                                purpose,

                                (
                                    institution
                                    if institution
                                    else None
                                ),

                                (
                                    request_notes
                                    if request_notes
                                    else None
                                ),

                                delivery_method,

                                payment_method,
                            ]
                        )

                        document_request_id = (
                            cursor.lastrowid
                        )

                    if not document_request_id:

                        raise Exception(
                            "Unable to retrieve "
                            "new document request ID."
                        )

                    # =================================
                    # GET CREATED DATE
                    # =================================

                    with connection.cursor() as cursor:

                        cursor.execute(
                            """
                            SELECT
                                created_at

                            FROM document_requests

                            WHERE
                                request_id = %s

                            LIMIT 1
                            """,
                            [
                                document_request_id
                            ]
                        )

                        created_row = (
                            cursor.fetchone()
                        )

                    created_at = (

                        created_row[0]

                        if created_row

                        else None
                    )

                    # =================================
                    # GENERATE REFERENCE
                    # =================================

                    reference_number = (
                        build_document_request_reference(
                            document_request_id,
                            created_at
                        )
                    )

                    # =================================
                    # SAVE REFERENCE
                    # =================================

                    with connection.cursor() as cursor:

                        cursor.execute(
                            """
                            UPDATE document_requests

                            SET
                                reference_number = %s,
                                updated_at = NOW()

                            WHERE
                                request_id = %s
                            """,
                            [
                                reference_number,
                                document_request_id,
                            ]
                        )

                    # =================================
                    # SAVE ATTACHMENTS
                    # =================================

                    if attachment_files:

                        saved_attachment_paths = (
                            save_document_request_attachments(
                                document_request_id,
                                attachment_files
                            )
                        )

                # =====================================
                # SUCCESS
                # =====================================

                messages.success(
                    request,
                    (
                        "Your document request "
                        "has been submitted "
                        "successfully. "
                        "Reference number: "
                        f"{reference_number}"
                    )
                )

                return redirect(
                    "request_document"
                )

            except Exception as e:

                # =====================================
                # DELETE SAVED FILES
                # =====================================

                for saved_path in (
                    saved_attachment_paths
                ):

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
                    "DOCUMENT REQUEST "
                    "INSERT ERROR:",
                    e
                )

                messages.error(
                    request,
                    "Unable to submit your "
                    "document request. "
                    "Please try again."
                )

    # =================================================
    # RECENT REQUESTS
    # =================================================

    recent_requests = []

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    dr.request_id,
                    dr.reference_number,

                    dt.type_name,

                    dr.purpose,
                    dr.institution,
                    dr.request_notes,

                    dr.delivery_method,
                    dr.payment_method,

                    dr.status,

                    dr.created_at,
                    dr.updated_at,

                    (
                        SELECT COUNT(*)

                        FROM
                            document_request_attachments dra

                        WHERE
                            dra.request_id =
                            dr.request_id

                    ) AS attachment_count

                FROM document_requests dr

                INNER JOIN document_types dt
                    ON
                        dt.document_type_id =
                        dr.document_type_id

                WHERE
                    dr.resident_id = %s

                ORDER BY
                    dr.created_at DESC

                LIMIT 5
                """,
                [
                    resident_id
                ]
            )

            rows = cursor.fetchall()

        for row in rows:

            request_id = row[0]

            reference_number = (
                row[1]
                or
                build_document_request_reference(
                    request_id,
                    row[9]
                )
            )

            recent_requests.append({

                "request_id":
                    request_id,

                "reference_number":
                    reference_number,

                "document_name":
                    row[2],

                "purpose":
                    row[3],

                "institution":
                    row[4],

                "request_notes":
                    row[5],

                "delivery_method":
                    row[6],

                "payment_method":
                    row[7],

                "status":
                    row[8],

                "created_at":
                    row[9],

                "updated_at":
                    row[10],

                "attachment_count":
                    row[11] or 0,
            })

    except Exception as e:

        print(
            "RECENT DOCUMENT REQUEST "
            "LOAD ERROR:",
            e
        )

        messages.error(
            request,
            "Unable to load your recent "
            "document requests."
        )

    # =================================================
    # STATISTICS
    # =================================================

    total_request_count = 0
    active_request_count = 0
    ready_request_count = 0

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT

                    COUNT(*),

                    COALESCE(
                        SUM(
                            CASE

                                WHEN status IN
                                (
                                    'Submitted',
                                    'Under Verification',
                                    'Ready for Signature'
                                )

                                THEN 1

                                ELSE 0

                            END
                        ),
                        0
                    ),

                    COALESCE(
                        SUM(
                            CASE

                                WHEN status =
                                    'Ready for Pickup'

                                THEN 1

                                ELSE 0

                            END
                        ),
                        0
                    )

                FROM document_requests

                WHERE
                    resident_id = %s
                """,
                [
                    resident_id
                ]
            )

            statistics = (
                cursor.fetchone()
            )

        if statistics:

            total_request_count = (
                statistics[0] or 0
            )

            active_request_count = (
                statistics[1] or 0
            )

            ready_request_count = (
                statistics[2] or 0
            )

    except Exception as e:

        print(
            "DOCUMENT REQUEST "
            "STATISTICS ERROR:",
            e
        )

    # =================================================
    # CONTEXT
    # =================================================

    context.update({

        "resident":
            resident,

        "document_types":
            document_types,

        "delivery_methods":
            delivery_methods,

        "payment_methods":
            payment_methods,

        "form_data":
            form_data,

        "recent_requests":
            recent_requests,

        "total_request_count":
            total_request_count,

        "active_request_count":
            active_request_count,

        "ready_request_count":
            ready_request_count,
    })

    # =================================================
    # RENDER
    # =================================================

    return render(
        request,
        "website/request_document.html",
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
    # GET RESIDENT
    # =================================================

    resident = get_resident_by_user_id(
        user_id
    )

    if not resident:

        messages.error(
            request,
            "Your resident profile could not be found."
        )

        return redirect(
            "home"
        )

    # =================================================
    # PREPARE RESIDENT PROFILE
    # =================================================

    resident = prepare_resident_profile(
        resident
    )

    # =================================================
    # CONTEXT
    # =================================================

    context.update({

        "resident":
            resident,

    })

    # =================================================
    # RENDER
    # =================================================

    return render(
        request,
        "website/my_profile.html",
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