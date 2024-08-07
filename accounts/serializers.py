from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from dj_rest_auth.serializers import (
    LoginSerializer,
    UserDetailsSerializer,
    PasswordResetSerializer,
)
from phonenumber_field.serializerfields import PhoneNumberField
from .forms import CustomPasswordResetForm


User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["email", "password"]
        extra_kwargs = {
            "password": {
                "write_only": True,
            }
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"], password=validated_data["password"]
        )
        return user


class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField()

    def validate_otp_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                "OTP should consist only of numeric values."
            )
        if len(value) != 6:
            raise serializers.ValidationError(
                "OTP should be exactly 6 characters long."
            )
        return value


class ResendVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class CustomLoginSerializer(LoginSerializer):
    """
    Overriding LoginSerializer from dj_rest_auth package so that
    there is no need for users to input username when they want to sign in.
    """

    username = None

    def validate_email_verification_status(self, user, email=None):
        if not user.is_verified:
            raise ValidationError(
                _(
                    "E-mail is not verified. Please check your email for verification code or if you did not receive verification code try to resend it once again."
                )
            )

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        password = attrs.get("password")
        user = self.get_auth_user(username, email, password)

        if not user:
            msg = _("Unable to log in with provided credentials.")
            raise ValidationError(msg)

        # Did we get back an active user?
        self.validate_auth_user_status(user)

        # Did we get back a verified user?
        self.validate_email_verification_status(user, email=email)

        attrs["user"] = user
        return attrs


class CustomUserDetailsSerializer(UserDetailsSerializer):
    """
    Overriding UserDetailsSerializer from dj_rest_auth package so that
    there are more fields included from the CustomUser model in the swagger docs.
    """

    is_verified = serializers.BooleanField(read_only=True)
    phone_number = PhoneNumberField(region="GE")

    class Meta(UserDetailsSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "phone_number",
            "birthdate",
            "address",
            "profile_image",
            "preferred_currency",
            "is_subscribed_to_newsletter",
            "is_verified",
        )
        read_only_fields = ["is_verified"]


class CustomPasswordResetSerializer(PasswordResetSerializer):
    @property
    def password_reset_form_class(self):
        return CustomPasswordResetForm

    def save(self):
        request = self.context.get("request")

        opts = {
            "use_https": request.is_secure(),
            "from_email": "example@mydomain.com",
            "request": request,
            "email_template_name": "password_reset_email.html",
        }

        self.reset_form.save(**opts)
