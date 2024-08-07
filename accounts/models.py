import uuid
from datetime import timedelta
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.db import models
from .managers import CustomUserManager


def expiration():
    return timezone.now() + timedelta(days=1)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    def user_profile_image_filename(self, filename):
        return f"profile_images/{self.id}-{filename}"

    CURRENCY_CHOICES = [
        ("GEL", "GEL"),
        ("USD", "USD"),
        ("EUR", "EUR"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=128, blank=True, null=True)
    phone_number = PhoneNumberField(max_length=13, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        upload_to=user_profile_image_filename,
        blank=True,
        null=True,
    )
    preferred_currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="GEL",
    )
    is_subscribed_to_newsletter = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class OTP(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)
    expiry_timestamp = models.DateTimeField(
        default=expiration, verbose_name="Expire on"
    )

    def __str__(self):
        return self.code

    def is_expired(self):
        return timezone.now() > self.expiry_timestamp

    class Meta:
        verbose_name = "OTP"
        verbose_name_plural = "OTPs"
