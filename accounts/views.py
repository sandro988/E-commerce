from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from dj_rest_auth.views import UserDetailsView, LogoutView
from drf_spectacular.utils import extend_schema
from accounts.serializers import (
    SignUpSerializer,
    OTPVerificationSerializer,
    ResendVerificationCodeSerializer,
    CustomUserDetailsSerializer,
)
from accounts.tasks import send_one_time_password_to_user, send_already_verified_email
from accounts.models import OTP, CustomUser
from openapi.account_examples import (
    retrieve_user_examples,
    update_user_account_examples,
    partial_update_user_account_examples,
)


class SignUpAPIView(CreateAPIView):
    """
    Endpoint for user registration.

    Accepts POST requests with user data in the request body. Creates a new user with the provided data if valid.

    Sends a one-time code to the user's email for account verification.
    Returns a success response with a message and status code 201 if successful.
    
    **Already authenticated users can not create new users.**
    """

    serializer_class = SignUpSerializer
    permission_classes = [
        AllowAny,
    ]

    def create(self, request, *args, **kwargs):
        # Authenticated should not be allowed to create new account.
        if request.user.is_authenticated:
            return Response(
                {
                    "message": "Authenticated users cannot create new accounts. Please sign out to proceed with sign up."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # Celery task for sending verification email to user.
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
                        "message": "User or OTP code is not correct. Please try again later."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            otp = OTP.objects.get(user__email=email, code=otp_code)
        except (CustomUser.DoesNotExist, OTP.DoesNotExist):
            return Response(
                {"message": "User or OTP code is not correct. Please try again later."},
                status=status.HTTP_404_NOT_FOUND,
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

        try:
            user = CustomUser.objects.get(email=email)
            if user.is_verified:
                send_already_verified_email.delay(email)
                return Response(
                    {"message": "Verification code resent successfully."},
                    status=status.HTTP_200_OK,
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
        except Exception as e:
            return Response(
                {"message": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CustomLogoutView(LogoutView):
    """
    Inherits from dj-rest-auth LogoutView and adds a check for already logged-out users.
    If the user is not authenticated, it returns a response indicating that they are already
    logged out. Otherwise, it proceeds with the original logout logic.
    """

    serializer_class = None

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

    @extend_schema(
        responses={
            200: CustomUserDetailsSerializer,
            401: CustomUserDetailsSerializer,
        },
        examples=retrieve_user_examples(),
    )
    def get(self, request, *args, **kwargs):
        """
        ## Retrieve user account details.

        This endpoint allows users to retrieve their account details.

        ### Fields:
        - **id (str)**: Universally Unique Identifier (UUID) representing the user's ID.
        - **email (str)**: User's email address.
        - **full_name (str)**: User's full name.
        - **phone_number (str)**: User's phone number.
        - **birthdate (str)**: User's birthdate in "YYYY-MM-DD" format.
        - **address (str)**: User's address.
        - **profile_image (str)**: Image or null if not set.
        - **preferred_currency (str)**: User's preferred currency.
        - **is_subscribed_to_newsletter (bool)**: Indicates whether the user is subscribed to the newsletter.
        - **is_verified (bool)**: Indicates whether the user's account is verified via email or not.

        ### Responses:
        - 200: Successful retrieval. Returns the user account data.
        - 401: Unauthorized. Authentication credentials were not provided or are invalid.
        - *For more information about responses, please refer to the examples below.*
        """
        return super().get(request, *args, **kwargs)

    @extend_schema(
        responses={
            200: CustomUserDetailsSerializer,
            400: CustomUserDetailsSerializer,
            401: CustomUserDetailsSerializer,
        },
        examples=update_user_account_examples(),
    )
    def put(self, request, *args, **kwargs):
        """
        ## Update user account.

        This endpoint allows users to update their account details.

        ### Request Body:
        - JSON object representing the updated user account.

        ### Fields:
        - **email (str)**: User's email address.
        - **full_name (str)**: User's full name.
        - **phone_number (str)**: User's phone number.
        - **birthdate (str)**: User's birthdate in "YYYY-MM-DD" format.
        - **address (str)**: User's address.
        - **profile_image (str)**: Image or null if not set.
        - **preferred_currency (str)**: User's preferred currency.
        - **is_subscribed_to_newsletter (bool)**: Indicates whether the user is subscribed to the newsletter.

        ### Responses:
        - 200: Successful update. Returns the updated user account data.
        - 400: Bad request. The request body is invalid or contains errors. See response body examples for details.
        - 401: Unauthorized. Authentication credentials were not provided or are invalid.
        - *For more information about responses, please refer to the examples below.*
        """
        if "is_verified" in request.data:
            return Response(
                {"error": "This field is read-only."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().put(request, *args, **kwargs)

    @extend_schema(
        responses={
            200: CustomUserDetailsSerializer,
            400: CustomUserDetailsSerializer,
            401: CustomUserDetailsSerializer,
        },
        examples=partial_update_user_account_examples(),
    )
    def patch(self, request, *args, **kwargs):
        """
        ## Update user account.

        This endpoint allows users to update their account details.

        ### Request Body:
        - JSON object representing the updated user account.

        ### Fields:
        - **email (str)**: User's email address.
        - **full_name (str)**: User's full name.
        - **phone_number (str)**: User's phone number.
        - **birthdate (str)**: User's birthdate in "YYYY-MM-DD" format.
        - **address (str)**: User's address.
        - **profile_image (str)**: Image or null if not set.
        - **preferred_currency (str)**: User's preferred currency.
        - **is_subscribed_to_newsletter (bool)**: Indicates whether the user is subscribed to the newsletter.

        ### Responses:
        - 200: Successful update. Returns the updated user account data.
        - 400: Bad request. The request body is invalid or contains errors. See response body examples for details.
        - 401: Unauthorized. Authentication credentials were not provided or are invalid.
        - *For more information about responses, please refer to the examples below.*
        """
        if "is_verified" in request.data:
            return Response(
                {"error": "This field is read-only."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().patch(request, *args, **kwargs)
