from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail

from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model
)

from django.contrib.auth.decorators import (
    login_required,
    user_passes_test
)

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.utils import timezone

from django.core.paginator import Paginator


from .models import (
    UserProfile,
    LoginActivity
)


import secrets
import time
import re


# Use custom user model safely
User = get_user_model()

# ==========================================
# LOGIN
# ==========================================


User = get_user_model()


def login_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        try:

            user = User.objects.get(
                username=username
            )

        except User.DoesNotExist:

            LoginActivity.objects.create(

                username=username,

                authentication_status="FAILED",

                reason="Username does not exist"

            )

            messages.error(
                request,
                "Invalid username or password."
            )

            return redirect(
                "login"
            )

        profile, created = UserProfile.objects.get_or_create(
            user=user
        )

        # ==============================
        # CHECK ACCOUNT LOCK
        # ==============================

        if profile.account_locked():

            LoginActivity.objects.create(

                user=user,

                username=username,

                authentication_status="FAILED",

                reason="Account is locked"

            )

            messages.error(
                request,
                "Account is locked. Contact administrator."
            )

            return redirect(
                "login"
            )

        authenticated_user = authenticate(

            request,

            username=username,

            password=password

        )

        # ==============================
        # WRONG PASSWORD
        # ==============================

        if authenticated_user is None:

            profile.failed_login_attempts += 1

            profile.save()

            LoginActivity.objects.create(

                user=user,

                username=username,

                authentication_status="FAILED",

                reason="Incorrect password"

            )

            if profile.failed_login_attempts >= 5:

                profile.is_locked = True

                profile.lock_reason = (
                    "Maximum failed login attempts reached"
                )

                profile.locked_at = timezone.now()

                profile.save()

                messages.error(
                    request,
                    "Account locked because of multiple failed attempts."
                )

            else:

                remaining = (
                    5 - profile.failed_login_attempts
                )

                messages.error(

                    request,

                    f"Incorrect password. {remaining} attempts remaining."

                )

            return redirect(
                "login"
            )

        if not user.email:

            messages.error(
                request,
                "No email registered."
            )

            return redirect(
                "login"
            )

        # CREATE OTP

        otp = str(
            secrets.randbelow(900000) + 100000
        )

        request.session["otp"] = otp

        request.session["otp_created"] = time.time()

        request.session["user_id"] = user.id

        try:

            send_mail(

                subject="Secure Login Verification",


                message=f"""
Hello {user.username},

Your One-Time Password (OTP) is:

{otp}

This code is required to complete your login.

Secure Authentication System
""",


                from_email=None,


                recipient_list=[
                    user.email
                ],


                fail_silently=False

            )

        except Exception as e:

            messages.error(

                request,

                f"Unable to send OTP: {e}"

            )

            return redirect(
                "login"
            )

        return redirect(
            "verify_otp"
        )

    return render(
        request,
        "accounts/login.html"
    )


# ==========================================
# VERIFY OTP
# ==========================================

def verify_otp(request):

    otp_created = request.session.get(
        "otp_created"
    )

    remaining_time = 0

    if otp_created:

        remaining_time = max(
            0,
            300 - int(time.time() - otp_created)
        )

    if request.method == "POST":

        entered_otp = request.POST.get(
            "otp"
        )

        saved_otp = request.session.get(
            "otp"
        )

        otp_created = request.session.get(
            "otp_created"
        )

        if not saved_otp or not otp_created:

            messages.error(
                request,
                "OTP session expired. Please login again."
            )

            return redirect(
                "login"
            )

        if time.time() - otp_created > 300:

            messages.error(
                request,
                "OTP expired. Please login again."
            )

            request.session.flush()

            return redirect(
                "login"
            )

        # ==============================
        # OTP SUCCESS
        # ==============================

        if entered_otp == saved_otp:

            user = User.objects.get(
                id=request.session["user_id"]
            )

            login(
                request,
                user
            )

            # CREATE SUCCESS LOGIN LOG

            LoginActivity.objects.create(

                user=user,

                username=user.username,

                authentication_status="SUCCESS",

                reason="OTP verified. Login successful."

            )

            # CLEAR OTP SESSION

            request.session.pop(
                "otp",
                None
            )

            request.session.pop(
                "otp_created",
                None
            )

            request.session.pop(
                "user_id",
                None
            )

            # ROLE REDIRECT

            if user.is_staff:

                return redirect(
                    "admin_dashboard"
                )

            else:

                return redirect(
                    "dashboard"
                )

        else:

            # WRONG OTP

            LoginActivity.objects.create(

                user=User.objects.get(
                    id=request.session["user_id"]
                ),

                username=User.objects.get(
                    id=request.session["user_id"]
                ).username,

                authentication_status="FAILED",

                reason="Incorrect OTP"

            )

            messages.error(
                request,
                "Invalid OTP."
            )

    return render(

        request,

        "accounts/verify_otp.html",

        {

            "remaining_time": remaining_time

        }

    )

# ==========================================
# RESEND OTP
# ==========================================


def resend_otp(request):

    user_id = request.session.get("user_id")

    if not user_id:

        messages.error(
            request,
            "Your login session expired."
        )

        return redirect("login")

    user = User.objects.get(id=user_id)

    otp = str(
        secrets.randbelow(900000) + 100000
    )

    request.session["otp"] = otp
    request.session["otp_created"] = time.time()

    try:

        send_mail(

            subject="Secure Login Verification",

            message=f"""
Hello {user.username},

Your new One-Time Password (OTP) is:

{otp}

Secure Authentication System
""",

            from_email=None,

            recipient_list=[
                user.email
            ],

            fail_silently=False

        )

        messages.success(
            request,
            "New OTP sent."
        )

    except Exception:

        messages.error(
            request,
            "Unable to resend OTP."
        )

    return redirect("verify_otp")


# ==========================================
# REGISTER
# ==========================================

def register_view(request):

    if request.method == "POST":

        first_name = request.POST.get(
            "first_name"
        )

        last_name = request.POST.get(
            "last_name"
        )

        username = request.POST.get(
            "username"
        )

        email = request.POST.get(
            "email"
        )

        password = request.POST.get(
            "password"
        )

        confirm_password = request.POST.get(
            "confirm_password"
        )

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("register")

        if len(password) < 12:

            messages.error(
                request,
                "Password must contain at least 12 characters."
            )

            return redirect("register")

        if not re.search("[A-Z]", password):

            messages.error(
                request,
                "Password must contain uppercase letter."
            )

            return redirect("register")

        if not re.search("[a-z]", password):

            messages.error(
                request,
                "Password must contain lowercase letter."
            )

            return redirect("register")

        if not re.search("[0-9]", password):

            messages.error(
                request,
                "Password must contain a number."
            )

            return redirect("register")

        if not re.search("[!@#$%^&*]", password):

            messages.error(
                request,
                "Password must contain special character."
            )

            return redirect("register")

        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return redirect("register")

        if User.objects.filter(email=email).exists():

            messages.error(
                request,
                "Email already registered."
            )

            return redirect("register")

        user = User.objects.create_user(

            username=username,

            email=email,

            password=password,

            first_name=first_name,

            last_name=last_name

        )

        UserProfile.objects.create(
            user=user
        )

        messages.success(
            request,
            "Account created successfully."
        )

        return redirect("login")

    return render(
        request,
        "accounts/register.html"
    )


# ==========================================
# FORGOT PASSWORD
# ==========================================

def forgot_password(request):

    return render(
        request,
        "accounts/forgot_password.html"
    )


# ==========================================
# USER DASHBOARD
# ==========================================

@login_required(login_url="login")
def dashboard_view(request):

    user = request.user

    recent_activity = LoginActivity.objects.filter(
        user=user
    ).order_by(
        "-login_time"
    )[:5]

    context = {

        "username": user.username,

        "email": user.email,

        "recent_activity": recent_activity,

    }

    return render(
        request,
        "accounts/dashboard.html",
        context
    )

# ==========================================
# ADMIN SECURITY CHECK
# ==========================================


def admin_required(user):

    return (
        user.is_authenticated
        and user.is_staff
    )


# ==========================================
# ADMIN DASHBOARD
# ==========================================


@login_required(login_url="login")
@user_passes_test(admin_required)
def admin_dashboard(request):

    total_users = User.objects.count()

    active_users = User.objects.filter(
        is_active=True
    ).count()

    locked_accounts = UserProfile.objects.filter(
        is_locked=True
    ).count()

    failed_attempts = LoginActivity.objects.filter(
        authentication_status="FAILED"
    ).count()

    successful_logins = LoginActivity.objects.filter(
        authentication_status="SUCCESS"
    ).count()

    # ==============================
    # PAGINATION
    # ==============================

    logs = LoginActivity.objects.order_by(
        "-login_time"
    )

    paginator = Paginator(

        logs,

        10

    )

    page_number = request.GET.get(
        "page"
    )

    recent_activity = paginator.get_page(
        page_number
    )

    context = {


        "total_users":
            total_users,


        "active_users":
            active_users,


        "locked_accounts":
            locked_accounts,


        "failed_attempts":
            failed_attempts,


        "successful_logins":
            successful_logins,


        "recent_activity":
            recent_activity,


    }

    return render(

        request,

        "accounts/admin_dashboard.html",

        context

    )

# ==========================================
# LOGIN ACTIVITY LOGS
# ==========================================


@login_required(login_url="login")
@user_passes_test(admin_required)
def login_activity_logs(request):

    logs = LoginActivity.objects.all().order_by(
        "-login_time"
    )

    paginator = Paginator(
        logs,
        15
    )

    page = request.GET.get(
        "page"
    )

    activity_logs = paginator.get_page(
        page
    )

    context = {

        "activity_logs": activity_logs

    }

    return render(
        request,
        "accounts/login_activity.html",
        context
    )

# ==========================================
# LOGOUT
# ==========================================


def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("login")


# ==========================================
# USER MANAGEMENT
# ==========================================


# LIST USERS
@login_required(login_url="login")
@user_passes_test(admin_required)
def user_management(request):

    users = User.objects.all().order_by(
        "-date_joined"
    )

    context = {
        "users": users
    }

    return render(
        request,
        "accounts/user_management.html",
        context
    )


# ==========================================
# CREATE USER
# ==========================================

# ==========================================
# CREATE USER
# ==========================================

# ==========================================
# CREATE USER
# ==========================================

@login_required(login_url="login")
@user_passes_test(admin_required)
def create_user(request):

    if request.method == "POST":

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        username = request.POST.get("username")
        email = request.POST.get("email")

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # PASSWORD MATCH

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("create_user")

        # PASSWORD VALIDATION

        if len(password) < 12:

            messages.error(
                request,
                "Password must contain at least 12 characters."
            )

            return redirect("create_user")

        if not re.search("[A-Z]", password):

            messages.error(
                request,
                "Password must contain uppercase letter."
            )

            return redirect("create_user")

        if not re.search("[a-z]", password):

            messages.error(
                request,
                "Password must contain lowercase letter."
            )

            return redirect("create_user")

        if not re.search("[0-9]", password):

            messages.error(
                request,
                "Password must contain a number."
            )

            return redirect("create_user")

        if not re.search("[!@#$%^&*]", password):

            messages.error(
                request,
                "Password must contain special character."
            )

            return redirect("create_user")

        # CHECK USERNAME

        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return redirect("create_user")

        # CHECK EMAIL

        if User.objects.filter(email=email).exists():

            messages.error(
                request,
                "Email already registered."
            )

            return redirect("create_user")

        # CREATE USER

        user = User.objects.create_user(

            username=username,

            email=email,

            password=password,

            first_name=first_name,

            last_name=last_name

        )

        # CREATE PROFILE

        UserProfile.objects.create(
            user=user
        )

        messages.success(
            request,
            "User created successfully."
        )

        return redirect(
            "user_management"
        )

    # IMPORTANT
    # Handles GET request

    return render(
        request,
        "accounts/create_user.html"
    )


# ==========================================
# EDIT USER
# ==========================================

@login_required(login_url="login")
@user_passes_test(admin_required)
def edit_user(request, user_id):

    user = get_object_or_404(
        User,
        id=user_id
    )

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        email = request.POST.get(
            "email"
        )

        user.username = username

        user.email = email

        user.save()

        messages.success(
            request,
            "User updated successfully."
        )

        return redirect(
            "user_management"
        )

    context = {

        "user": user

    }

    return render(
        request,
        "accounts/edit_user.html",
        context
    )


# ==========================================
# DELETE USER
# ==========================================

@login_required(login_url="login")
@user_passes_test(admin_required)
def delete_user(request, user_id):

    user = get_object_or_404(
        User,
        id=user_id
    )

    # PREVENT DELETE ADMIN

    if user.is_superuser:

        messages.error(
            request,
            "Cannot delete administrator account."
        )

    else:

        user.delete()

        messages.success(
            request,
            "User deleted successfully."
        )

    return redirect(
        "user_management"
    )


# ==========================================
# LOCKED ACCOUNTS
# ==========================================


@login_required(login_url="login")
@user_passes_test(admin_required)
def locked_accounts(request):

    locked_users = User.objects.filter(
        userprofile__is_locked=True
    ).select_related("userprofile")

    return render(
        request,
        "accounts/locked_accounts.html",
        {
            "locked_users": locked_users
        }
    )


# ==========================================
# UNLOCK USER
# ==========================================


@login_required(login_url="login")
@user_passes_test(admin_required)
def unlock_account(request, user_id):

    user = get_object_or_404(User, id=user_id)

    profile = user.userprofile

    profile.failed_login_attempts = 0
    profile.is_locked = False
    profile.lock_reason = None
    profile.locked_at = None

    profile.save()

    return redirect("locked_accounts")
