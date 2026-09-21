from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, transaction
from datetime import datetime


# =====================================================
# HOME
# =====================================================

def home(request):

    user_id = request.session.get("user_id")

    context = {
        "user_id": user_id,
        "username": request.session.get("username", ""),
        "email": request.session.get("email", ""),
        "role": request.session.get("role", ""),
    }

    return render(
        request,
        "website/home.html",
        context
    )


# =====================================================
# DASHBOARD
# =====================================================

def dashboard(request):

    return render(
        request,
        "website/dashboard.html"
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

    resident = None

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


    # =================================================
    # CREATE RESIDENT DATA
    # =================================================

    if row:

        resident = {

            "resident_id": row[0],

            "first_name": row[1],

            "middle_name": row[2],

            "last_name": row[3],

            "suffix": row[4],

            "email": row[5],

            "contact_number": row[6],

            "address": row[7],

        }


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
                {
                    "user_id": user_id,
                    "username": username,
                    "email": email,
                    "role": role,
                    "resident": resident,
                }
            )


        if not subject:

            messages.error(
                request,
                "Please enter a subject."
            )

            return render(
                request,
                "website/submit_complaint.html",
                {
                    "user_id": user_id,
                    "username": username,
                    "email": email,
                    "role": role,
                    "resident": resident,
                }
            )


        if not description:

            messages.error(
                request,
                "Please provide a description."
            )

            return render(
                request,
                "website/submit_complaint.html",
                {
                    "user_id": user_id,
                    "username": username,
                    "email": email,
                    "role": role,
                    "resident": resident,
                }
            )


        if not location:

            messages.error(
                request,
                "Please enter the incident location."
            )

            return render(
                request,
                "website/submit_complaint.html",
                {
                    "user_id": user_id,
                    "username": username,
                    "email": email,
                    "role": role,
                    "resident": resident,
                }
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
                    {
                        "user_id": user_id,
                        "username": username,
                        "email": email,
                        "role": role,
                        "resident": resident,
                    }
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
                {
                    "user_id": user_id,
                    "username": username,
                    "email": email,
                    "role": role,
                    "resident": resident,
                }
            )


        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        messages.success(
            request,
            "Your complaint has been submitted successfully."
        )

        return render(
            request,
            "website/submit_complaint.html",
            {
                "user_id": user_id,
                "username": username,
                "email": email,
                "role": role,
                "resident": resident,
            }
        )

    # =================================================
    # DISPLAY FORM
    # =================================================

    context = {

        "user_id":
            user_id,

        "username":
            username,

        "email":
            email,

        "role":
            role,

        "resident":
            resident,

    }


    return render(
        request,
        "website/submit_complaint.html",
        context
    )


# =====================================================
# TRACK COMPLAINT
# =====================================================

def track_complaint(request):

    return render(
        request,
        "website/track_complaint.html"
    )


# =====================================================
# VERIFY DOCUMENT
# =====================================================

def verify_document(request):

    return render(
        request,
        "website/verify_document.html"
    )


# =====================================================
# ABOUT
# =====================================================

def about(request):

    return render(
        request,
        "website/about.html"
    )


# =====================================================
# CONTACT
# =====================================================

def contact(request):

    return render(
        request,
        "website/contact.html"
    )