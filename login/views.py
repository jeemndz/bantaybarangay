from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password

from .models import User


def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(
                username=username,
                is_active=True
            )

            if check_password(password, user.password_hash):

                request.session['user_id'] = user.user_id
                request.session['username'] = user.username
                request.session['role'] = user.role

                return redirect('resident_list')

            else:
                messages.error(
                    request,
                    'Invalid username or password.'
                )

        except User.DoesNotExist:

            messages.error(
                request,
                'Invalid username or password.'
            )

    return render(request, 'login/login.html')