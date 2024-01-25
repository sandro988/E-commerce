from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Manager for a custom user that will use email
    as an identifier instead of a username.
    """

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email is needed in order to create your account.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "With Superuser 'is_staff' field must have a value of True."
            )
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "With Superuser 'is_superuser' field must have a value of True."
            )

        return self.create_user(email, password, **extra_fields)
