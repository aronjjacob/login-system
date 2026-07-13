from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [

    path(
        "",
        views.login_view,
        name="login"
    ),


    path(
        "register/",
        views.register_view,
        name="register"
    ),


    path(
        "forgot-password/",
        views.forgot_password_view,
        name="forgot_password"
    ),

    path("forgot-password/", views.forgot_password_view, name="forgot_password"),
        path("reset-password-confirm/", views.password_reset_confirm_view, name="password_reset_confirm"),

    path(
        "dashboard/",
        views.dashboard_view,
        name="dashboard"
    ),

    path(
        "test-email/",
        views.test_email,
        name="test_email",
    ),
    
    path("verify-otp/", views.verify_otp, name="verify_otp"),
]