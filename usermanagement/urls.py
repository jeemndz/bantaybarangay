from django.urls import path

from . import views


app_name = "usermanagement"


urlpatterns = [

    path(
        "",
        views.user_list,
        name="user_list"
    ),

]