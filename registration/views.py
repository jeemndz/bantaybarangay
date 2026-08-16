from django.shortcuts import render, redirect


def registration(request):
    if request.method == "POST":

        # Store Step 1 data in session
        request.session["registration_data"] = {
            "full_name": request.POST.get("full_name"),
            "birth_date": request.POST.get("birth_date"),
            "gender": request.POST.get("gender"),
            "civil_status": request.POST.get("civil_status"),
            "username": request.POST.get("username"),
            "password": request.POST.get("password"),
        }

        # Go to Step 2
        return redirect("step2_contact")

    return render(
        request,
        "registration/registration.html"
    )


def step2_contact(request):

    if request.method == "POST":

        # Get Step 1 data from session
        registration_data = request.session.get(
            "registration_data",
            {}
        )

        # Add Step 2 data
        registration_data.update({
            "mobile_number": request.POST.get("mobile_number"),
            "email": request.POST.get("email"),
            "house_block_lot": request.POST.get("house_block_lot"),
            "street_purok_sitio": request.POST.get("street_purok_sitio"),
            "province": request.POST.get("province"),
            "municipality_city": request.POST.get("municipality_city"),
            "barangay": request.POST.get("barangay"),
            "zip_code": request.POST.get("zip_code"),
        })

        # Save updated registration data
        request.session["registration_data"] = registration_data


    return render(
        request,
        "registration/step2_contact.html"
    )