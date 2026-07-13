from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse

import random
import secrets
import time
import re

from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model


User = get_user_model()


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:

            messages.error(
                request,
                "Invalid username or password."
            )

            return redirect("login")


        if not user.email:

            messages.error(
                request,
                "This account has no email address registered."
            )

            return redirect("login")


        otp = str(secrets.randbelow(900000) + 100000)

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

If you did not request this login, simply ignore this email.

Secure Authentication System
""",
                from_email=None,
                recipient_list=[user.email],
                fail_silently=False,
            )

        except Exception as e:

            messages.error(
                request,
                f"Unable to send OTP email.\n{e}"
            )

            return redirect("login")


        return redirect("verify_otp")


    return render(
        request,
        "accounts/login.html"
    )



def verify_otp(request):

    if request.method == "POST":

        entered_otp = request.POST.get("otp")

        saved_otp = request.session.get("otp")
        otp_created = request.session.get("otp_created")


        if not saved_otp or not otp_created:

            messages.error(
                request,
                "OTP session expired. Please login again."
            )

            return redirect("login")


        if time.time() - otp_created > 300:

            messages.error(
                request,
                "OTP expired. Please request a new login."
            )

            request.session.pop("otp", None)
            request.session.pop("otp_created", None)
            request.session.pop("user_id", None)

            return redirect("login")


        if entered_otp == saved_otp:

            user = User.objects.get(
                id=request.session["user_id"]
            )

            login(request, user)


            request.session.pop("otp", None)
            request.session.pop("otp_created", None)
            request.session.pop("user_id", None)


            return redirect("dashboard")


        else:

            messages.error(
                request,
                "Invalid OTP."
            )


    return render(
        request,
        "accounts/verify_otp.html"
    )



def register_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")


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
                "Password must contain an uppercase letter."
            )

            return redirect("register")


        if not re.search("[a-z]", password):

            messages.error(
                request,
                "Password must contain a lowercase letter."
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
                "Password must contain a special character."
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
                "Email is already registered."
            )

            return redirect("register")


        User.objects.create_user(
            username=username,
            email=email,
            password=password
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



def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        
        if email:
            # 1. Build the absolute URL for the reset page
            # (or your custom password reset confirm view)
            reset_path = reverse("password_reset_confirm")
            reset_url = request.build_absolute_uri(reset_path)

            # 2. Compose the email subject and message
            subject = "Password Reset Request"
            message = f"""Hi,

You requested a password reset for your account.

Click the link below to reset your password:
{reset_url}

If you did not make this request, please ignore this email.
"""

            # 3. Send the email
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.success(request, f"Password reset instructions have been sent to {email}.")
            except Exception as e:
                messages.error(request, f"Failed to send email. Error: {e}")

            return redirect("forgot_password")

    return render(request, "accounts/forgot_password.html")


def password_reset_confirm_view(request):
    """
    Renders the page where the user inputs their new password.
    """
    if request.method == "POST":
        email = request.POST.get("email")  # or pass user identifier via token/URL
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Basic validation
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "accounts/password_reset_confirm.html")

        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, "accounts/password_reset_confirm.html")

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            messages.success(request, "Your password has been successfully reset! You can now log in.")
            return redirect("login")
        except User.DoesNotExist:
            messages.error(request, "No account found with that email address.")
            return render(request, "accounts/password_reset_confirm.html")

    return render(request, "accounts/password_reset_confirm.html")


def dashboard_view(request):

    return render(
        request,
        "accounts/dashboard.html"
    )



def test_email(request):

    send_mail(
        subject="SMTP Test",
        message="Congratulations! Gmail SMTP is working correctly.",
        from_email=None,
        recipient_list=["jacobkolera@gmail.com"],
        fail_silently=False,
    )

    return HttpResponse("Email sent successfully!")