from django.utils.translation import gettext as _
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from dj_rest_auth.views import UserDetailsView, LogoutView
from accounts.serializers import (
    SignUpSerializer,
    OTPVerificationSerializer,
    ResendVerificationCodeSerializer,
    CustomUserDetailsSerializer,
)
from accounts.tasks import send_one_time_password_to_user
from accounts.models import OTP, CustomUser
from accounts.decorators import user_endpoint_docstring


class SignUpAPIView(CreateAPIView):
    """
    Endpoint for user registration.

    Accepts POST requests with user data in the request body. Creates a new user with the provided data if valid.

    Sends a one-time code to the user's email for account verification.
    Returns a success response with a message and status code 201 if successful.
    """

    serializer_class = SignUpSerializer
    permission_classes = [
        AllowAny,
    ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # Celery task for resending verification email to user.
        send_one_time_password_to_user.delay(user.id)

        return Response(
            {
                "message": "Successfully created a new user. One time code has been sent to your email, use it to verify your account."
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        user = serializer.save()
        return user


class OTPVerificationView(APIView):
    """
    API View for verifying a user based on an OTP code.
    This view allows users to verify their accounts by providing a valid OTP code
    along with their email. If the provided OTP code is valid and the user is not
    already verified, the user will be marked as verified.
    """

    serializer_class = OTPVerificationSerializer
    permission_classes = [
        AllowAny,
    ]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        otp_code = serializer.validated_data["otp_code"]

        try:
            user = CustomUser.objects.get(email=email)
            if user.is_verified:
                return Response(
                    {
                        "message": "User is already verified, you can not reverify an already verified user."
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            otp = OTP.objects.get(user__email=email, code=otp_code)
            if otp.expiry_timestamp < timezone.now():
                otp.delete()
                return Response(
                    {
                        "message": "OTP code has expired. Please request a new verification code."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except CustomUser.DoesNotExist:
            return Response(
                {"message": "User not found."}, status=status.HTTP_400_BAD_REQUEST
            )
        except OTP.DoesNotExist:
            return Response(
                {"message": "Invalid OTP code."}, status=status.HTTP_400_BAD_REQUEST
            )

        otp.user.is_verified = True
        otp.user.save()
        otp.delete()

        return Response(
            {"message": "User successfully verified."}, status=status.HTTP_200_OK
        )


class ResendVerificationCodeView(APIView):
    """
    API View for resending a verification code to a user.
    This view allows users to request a new verification code if they did not
    receive the initial code or if the code has expired.
    """

    serializer_class = ResendVerificationCodeSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        if not email:
            return Response(
                {"message": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(email=email)
            if user.is_verified:
                return Response(
                    {"message": "User is already verified."},
                    status=status.HTTP_409_CONFLICT,
                )

            # Celery task for resending verification email to user.
            send_one_time_password_to_user.delay(user.id)

            return Response(
                {"message": "Verification code resent successfully."},
                status=status.HTTP_200_OK,
            )

        except CustomUser.DoesNotExist:
            return Response(
                {"message": "User not found."}, status=status.HTTP_400_BAD_REQUEST
            )


class CustomLogoutView(LogoutView):
    """
    Inherits from dj-rest-auth LogoutView and adds a check for already logged-out users.
    If the user is not authenticated, it returns a response indicating that they are already
    logged out. Otherwise, it proceeds with the original logout logic.
    """

    def logout(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": _("You are already logged out.")},
                status=status.HTTP_200_OK,
            )

        response = super().logout(request)
        return response


class CustomUserDetailsView(UserDetailsView):
    parser_classes = (JSONParser, MultiPartParser)
    serializer_class = CustomUserDetailsSerializer

    def get_serializer_class(self):
        if self.request.method == "PUT" or self.request.method == "PATCH":
            # Excluding the 'is_verified' field from serializer for PUT and PATCH methods.
            # Users should be able to see if they are verified or not, but should not be able to modify verification status.
            class SerializerClass(CustomUserDetailsSerializer):
                class Meta(CustomUserDetailsSerializer.Meta):
                    fields = [
                        field
                        for field in CustomUserDetailsSerializer.Meta.fields
                        if field != "is_verified"
                    ]

            return SerializerClass
        return self.serializer_class

    @user_endpoint_docstring("API endpoint for User retrieval.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @user_endpoint_docstring(
        "API endpoint for User update.",
        exclude_fields=["id", "email", "is_verified"],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @user_endpoint_docstring(
        "API endpoint for partial user update.",
        exclude_fields=["id", "email", "is_verified"],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
