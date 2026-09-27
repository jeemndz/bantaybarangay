from django.urls import path
from . import views


urlpatterns = [

    # =========================================================
    # LOGIN
    # =========================================================

    path(
        "",
        views.login_view,
        name="login"
    ),


    # =========================================================
    # FORGOT PASSWORD
    # =========================================================

    path(
        "forgot-password/",
        views.forgot_password_view,
        name="forgot_password"
    ),


    # =========================================================
    # LOGOUT
    # =========================================================

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

]