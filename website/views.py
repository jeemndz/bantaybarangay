from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, transaction
from datetime import datetime


# =====================================================
# HELPER: SESSION CONTEXT
# =====================================================

def get_session_context(request):
    """
    Returns the common logged-in user information
    stored in the Django session.
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
    Finds the resident record connected to the
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
                address
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
    }


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
    # SESSION INFORMATION
    # =================================================

    username = request.session.get(
        "username",
        ""
    )

    email = request.session.get(
        "email",
        ""
    )

    role = request.session.get(
        "role",
        ""
    )


    # =================================================
    # FIND RESIDENT
    # =================================================

    resident = get_resident_by_user_id(user_id)


    # =================================================
    # RESIDENT NOT FOUND
    # =================================================

    if not resident:

        messages.error(
            request,
            "Your resident profile could not be found."
        )

        return redirect("home")


    # =================================================
    # BASE CONTEXT
    # =================================================

    context = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "role": role,
        "resident": resident,
    }


    # =================================================
    # POST REQUEST
    # =================================================

    if request.method == "POST":

        # -------------------------------------------------
        # GET FORM DATA
        # -------------------------------------------------

        complaint_type = request.POST.get(
            "complaint_type",
            ""
        ).strip()

        subject = request.POST.get(
            "subject",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        location = request.POST.get(
            "location",
            ""
        ).strip()

        incident_date = request.POST.get(
            "incident_date",
            ""
        ).strip()

        incident_time = request.POST.get(
            "incident_time",
            ""
        ).strip()

        priority = request.POST.get(
            "priority",
            "Medium"
        ).strip()


        # =================================================
        # KEEP FORM DATA
        # =================================================

        context["form_data"] = {
            "complaint_type": complaint_type,
            "subject": subject,
            "description": description,
            "location": location,
            "incident_date": incident_date,
            "incident_time": incident_time,
            "priority": priority,
        }


        # =================================================
        # VALIDATION
        # =================================================

        if not complaint_type:

            messages.error(
                request,
                "Please select a complaint type."
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


        # =================================================
        # CREATE INCIDENT DATETIME
        # =================================================

        incident_datetime = None

        if incident_date:

            try:

                if incident_time:

                    incident_datetime = datetime.strptime(
                        f"{incident_date} {incident_time}",
                        "%Y-%m-%d %H:%M"
                    )

                else:

                    incident_datetime = datetime.strptime(
                        incident_date,
                        "%Y-%m-%d"
                    )

            except ValueError:

                messages.error(
                    request,
                    "Invalid incident date or time."
                )

                return render(
                    request,
                    "website/submit_complaint.html",
                    context
                )


        # =================================================
        # INSERT COMPLAINT
        # =================================================

        try:

            with transaction.atomic():

                with connection.cursor() as cursor:

                    cursor.execute(
                        """
                        INSERT INTO complaints
                        (
                            resident_id,
                            complaint_type,
                            subject,
                            description,
                            location,
                            incident_date,
                            priority,
                            status,
                            submitted_at
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
                            'Submitted',
                            NOW()
                        )
                        """,
                        [
                            resident["resident_id"],
                            complaint_type,
                            subject,
                            description,
                            location,
                            incident_datetime,
                            priority,
                        ]
                    )


        except Exception as e:

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
        # SUCCESS
        # =================================================

        messages.success(
            request,
            "Your complaint has been submitted successfully."
        )

        # Prevent duplicate submission if page is refreshed
        return redirect("submit_complaint")


    # =================================================
    # DISPLAY FORM
    # =================================================

    return render(
        request,
        "website/submit_complaint.html",
        context
    )


# =====================================================
# TRACK COMPLAINT
# =====================================================

def track_complaint(request):

    context = get_session_context(request)

    return render(
        request,
        "website/track_complaint.html",
        context
    )


# =====================================================
# VERIFY DOCUMENT
# =====================================================

def verify_document(request):

    context = get_session_context(request)

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

    user_id = request.session.get("user_id")

    if not user_id:

        messages.error(
            request,
            "Please log in first before requesting a document."
        )

        return redirect("login")


    # =================================================
    # SESSION INFORMATION
    # =================================================

    context = get_session_context(request)


    # =================================================
    # FIND RESIDENT
    # =================================================

    resident = get_resident_by_user_id(user_id)

    if not resident:

        messages.error(
            request,
            "Your resident profile could not be found."
        )

        return redirect("home")


    context["resident"] = resident


    # =================================================
    # DISPLAY DOCUMENT REQUEST PAGE
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

    context = get_session_context(request)

    return render(
        request,
        "website/about.html",
        context
    )


# =====================================================
# CONTACT
# =====================================================

def contact(request):

    context = get_session_context(request)

    return render(
        request,
        "website/contact.html",
        context
    )