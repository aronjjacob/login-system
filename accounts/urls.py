from django.urls import path
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
        views.forgot_password,
        name="forgot_password"
    ),
    
    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),


    path(
        "user-management/",
        views.user_management,
        name="user_management"
    ),


    path(
        "create-user/",
        views.create_user,
        name="create_user"
    ),


    path(
        "edit-user/<int:user_id>/",
        views.edit_user,
        name="edit_user"
    ),


    path(
        "delete-user/<int:user_id>/",
        views.delete_user,
        name="delete_user"
    ),


    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    path(
        "locked-accounts/",
        views.locked_accounts,
        name="locked_accounts",
    ),

    path(
        "unlock/<int:user_id>/",
        views.unlock_account,
        name="unlock_account",
    ),
    
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    
    path(
        "resend-otp/",
        views.resend_otp,
        name="resend_otp"
    ),
]