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

    # ==========================
    # DJANGO BUILT-IN PASSWORD RESET
    # ==========================

    path(
        "forgot-password/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/forgot_password.html",
            email_template_name="accounts/password_reset_email.html",
            subject_template_name="accounts/password_reset_subject.txt",
        ),
        name="forgot_password",
    ),

    path(
        "forgot-password/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),

    # ==========================
    # ADMIN
    # ==========================

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
        "locked-accounts/",
        views.locked_accounts,
        name="locked_accounts"
    ),

    path(
        "unlock/<int:user_id>/",
        views.unlock_account,
        name="unlock_account"
    ),

    # ==========================
    # OTP
    # ==========================

    path(
        "verify-otp/",
        views.verify_otp,
        name="verify_otp"
    ),

    path(
        "resend-otp/",
        views.resend_otp,
        name="resend_otp"
    ),

    # ==========================
    # LOGOUT
    # ==========================

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    path(
        "dashboard/",
        views.dashboard_view,
        name="dashboard"
    ),

    path(
        "login-activity/",
        views.login_activity_logs,
        name="login_activity"
    ),

]

