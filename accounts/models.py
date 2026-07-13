from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class UserOTP(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    otp = models.CharField(
        max_length=6
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return self.user.username


# ==========================================
# USER SECURITY PROFILE
# ==========================================

class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    # Failed login attempts
    failed_login_attempts = models.IntegerField(
        default=0
    )

    # Automatic lock expires after 15 minutes
    locked_until = models.DateTimeField(
        null=True,
        blank=True
    )

    # Manual/Admin lock
    is_locked = models.BooleanField(
        default=False
    )

    lock_reason = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    # Force password reset after unlock (optional)
    password_reset_required = models.BooleanField(
        default=False
    )

    def account_locked(self):
        """
        Returns True if the account is currently locked.
        Checks both admin lock and temporary lock.
        """

        # Admin lock
        if self.is_locked:
            return True

        # Temporary lock
        if self.locked_until:
            return timezone.now() < self.locked_until

        return False

    def increase_attempts(self):
        """
        Called after every failed login.
        Locks account for 15 minutes after 5 failed attempts.
        """

        self.failed_login_attempts += 1

        if self.failed_login_attempts >= 5:

            self.locked_until = (
                timezone.now()
                + timedelta(minutes=15)
            )

            self.lock_reason = (
                "Maximum failed login attempts reached."
            )

        self.save()

    def reset_attempts(self):
        """
        Clears failed attempts after successful login
        or after admin unlock.
        """

        self.failed_login_attempts = 0
        self.locked_until = None
        self.lock_reason = None

        self.save()

    def admin_unlock(self):
        """
        Unlock account from Django Admin.
        """

        self.failed_login_attempts = 0
        self.locked_until = None
        self.is_locked = False
        self.lock_reason = None
        self.password_reset_required = False

        self.save()

    def __str__(self):
        return self.user.username


# ==========================================
# LOGIN ACTIVITY LOG
# ==========================================

class LoginActivity(models.Model):

    STATUS_CHOICES = (
        ("SUCCESS", "SUCCESS"),
        ("FAILED", "FAILED"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    username = models.CharField(
        max_length=150
    )

    login_time = models.DateTimeField(
        auto_now_add=True
    )

    authentication_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    reason = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username
    

class LoginLog(models.Model):

    STATUS_CHOICES = (
        ("SUCCESS", "SUCCESS"),
        ("FAILED", "FAILED"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    username = models.CharField(
        max_length=150
    )

    login_time = models.DateTimeField(
        auto_now_add=True
    )

    authentication_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )

    reason = models.CharField(
        max_length=255
    )


    def __str__(self):
        return f"{self.username} - {self.authentication_status}"