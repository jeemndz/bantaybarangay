from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, transaction
from datetime import datetime


# =====================================================
# HELPER: SESSION CONTEXT
# =====================================================

def get_session_context(request):
    """
    Return the common session information used by
    the website templates.
    """

    return {
        "user_id": request.session.get("user_id"),
        "username": request.session.get("username", ""),
        "email": request.session.get("email", ""),
        "role": request.session.get("role", ""),
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
            [user_id]
        )

        row = cursor.fetchone()

    if not row:
        return None

    return {
        "resident_id": row[0],
        "first_name": row[1],
        "middle_name": row[2],
        "last_name": row[3],
        "suffix": row[4],
        "email": row[5],
        "contact_number": row[6],
        "address": row[7],
        "verification_status": row[8],
    }


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

    return f"CMP-{year}-{complaint_id:04d}"


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
            "Your complaint has been submitted and is awaiting review.",

        "Under Review":
            "Your complaint is currently being reviewed by the barangay.",

        "Under Investigation":
            "Barangay officials are currently investigating this complaint.",

        "Resolved":
            "This complaint has been resolved.",

        "Rejected":
            "This complaint has been rejected. Contact the barangay for more information.",

        "Closed":
            "This complaint has been officially closed.",
    }

    return status_messages.get(
        status,
        "Your complaint is currently being processed."
    )


# =====================================================
# HOME
# =====================================================

def home(request):

    context = get_session_context(request)

    return render(
        request,
        "website/home.html",
        context
    )


# =====================================================
# DASHBOARD
# =====================================================

def dashboard(request):

    context = get_session_context(request)

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

    user_id = request.session.get("user_id")

    if not user_id:

        messages.error(
            request,
            "Please log in first before submitting a complaint."
        )

        return redirect("login")


    # =================================================
    # GET SESSION INFORMATION
    # =================================================

    context = get_session_context(request)


    # =================================================
    # CHECK USER ROLE
    # =================================================

    role = (
        context.get("role", "")
        .strip()
        .lower()
    )

    if role != "resident":

        messages.error(
            request,
            "Only resident accounts can submit complaints."
        )

        return redirect("home")


    # =================================================
    # GET RESIDENT PROFILE
    # =================================================

    resident = get_resident_by_user_id(
        user_id
    )

    if not resident:

        messages.error(
            request,
            "Your resident profile could not be found."
        )

        return redirect("home")


    # =================================================
    # DEFAULT TEMPLATE CONTEXT
    # =================================================

    context.update({
        "resident": resident,

        "form_data": {},

        # Success popup
        "complaint_submitted": False,
        "submitted_complaint": None,
        "submitted_complaint_id": "",
        "complaint_reference": "",
        "submitted_report_type": "",
        "submitted_complaint_type": "",
        "submitted_subject": "",
        "submitted_status": "",
    })


    # =================================================
    # GET REQUEST
    # =================================================
    #
    # This is where the popup information is retrieved
    # after a successful POST redirects back here.
    #
    # POST
    #   ↓
    # INSERT complaint
    #   ↓
    # Save submitted complaint to session
    #   ↓
    # redirect("submit_complaint")
    #   ↓
    # GET
    #   ↓
    # Read session
    #   ↓
    # complaint_submitted = True
    #   ↓
    # Popup is rendered
    #
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
                "complaint_submitted": True,

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
        # PRIORITY
        # =================================================
        #
        # Resident submissions start with N/A.
        # Barangay/admin staff can assign priority later.
        #
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

        if report_type not in allowed_report_types:

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
        #
        # Respondent information is only required for
        # Formal Complaints.
        #
        # Community Issues do not require a respondent.
        #
        # =================================================

        if report_type == "Formal Complaint":

            if not respondent_name:

                messages.error(
                    request,
                    "Please enter the respondent's name or known alias."
                )

                return render(
                    request,
                    "website/submit_complaint.html",
                    context
                )


            if not respondent_address:

                messages.error(
                    request,
                    "Please enter the respondent's address or known location."
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
        # INSERT COMPLAINT INTO DATABASE
        # =================================================

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
                            resident["resident_id"],

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


                    # =====================================
                    # GET DATABASE SUBMISSION DATE
                    # =====================================

                    cursor.execute(
                        """
                        SELECT
                            submitted_at
                        FROM complaints
                        WHERE complaint_id = %s
                        LIMIT 1
                        """,
                        [complaint_id]
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

            # Development/debug information
            print(
                "COMPLAINT INSERT ERROR:",
                e
            )

            messages.error(
                request,
                "Unable to submit your complaint. Please try again."
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
        #
        # IMPORTANT:
        #
        # We intentionally DO NOT use:
        #
        # messages.success(...)
        #
        # The custom complaint popup is controlled by
        # complaint_submitted instead.
        #
        # The information below survives the redirect.
        #
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
        }


        # Make sure Django knows the session changed.

        request.session.modified = True


        # =================================================
        # REDIRECT BACK TO SUBMIT PAGE
        # =================================================
        #
        # DO NOT redirect to my_complaints.
        #
        # The redirected GET will read the session and
        # display complaint_success_popup.html.
        #
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
        context.get("role", "")
        .strip()
        .lower()
    )

    if role != "resident":

        messages.error(
            request,
            "Only resident accounts can access My Complaints."
        )

        return redirect(
            "home"
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


    complaints = []


    # =================================================
    # LOAD COMPLAINTS
    # =================================================

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    complaint_id,
                    resident_id,
                    complaint_type,
                    subject,
                    description,
                    location,
                    incident_date,
                    priority,
                    status,
                    assigned_official,
                    resolution,
                    submitted_at,
                    updated_at,
                    report_type,
                    respondent_name,
                    respondent_address,
                    respondent_relationship,
                    respondent_contact,
                    incident_time
                FROM complaints
                WHERE resident_id = %s
                ORDER BY submitted_at DESC
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
            complaint["complaint_type"]

            for complaint in complaints

            if complaint["complaint_type"]
        }
    )


    # =================================================
    # RESIDENT FULL NAME
    # =================================================

    name_parts = [
        resident.get("first_name"),
        resident.get("middle_name"),
        resident.get("last_name"),
        resident.get("suffix"),
    ]


    resident_full_name = " ".join(
        part.strip()

        for part in name_parts

        if part and part.strip()
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
            "Please log in first before requesting a document."
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


    context["resident"] = resident


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