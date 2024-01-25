from django.urls import path
from dj_rest_auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
)
from .views import (
    SignUpAPIView,
    OTPVerificationView,
    CustomLogoutView,
    CustomUserDetailsView,
    ResendVerificationCodeView,
)

LoginView.__doc__ = """
Checks the credentials and returns the REST Token if the credentials are valid and authenticated. Calls Django Auth login method to register User ID in Django session framework.

Accepts the following POST parameters: `email`, `password`. 

Returns the REST Framework Token Object's key.
"""

PasswordChangeView.__doc__ = """
Accepts the following POST parameters: `old_password`, `new_password1`, `new_password2` Returns the success/fail message.
"""


urlpatterns = [
    path("login/", LoginView.as_view(), name="login_api_view"),
    path(
        "logout/",
        CustomLogoutView.as_view(http_method_names=["post"]),
        name="logout_api_view",
    ),
    path("signup/", SignUpAPIView.as_view(), name="signup_api_view"),
    path("verification/", OTPVerificationView.as_view(), name="verification_api_view"),
    path(
        "verification/resend/",
        ResendVerificationCodeView.as_view(),
        name="verification_resend_api_view",
    ),
    path("user/", CustomUserDetailsView.as_view(), name="user_details_api_view"),
    path(
        "password/change/",
        PasswordChangeView.as_view(),
        name="password_change_api_view",
    ),
    path(
        "password/reset/",
        PasswordResetView.as_view(),
        name="password_reset_api_view",
    ),
    path(
        "password/reset/confirm/<str:uidb64>/<str:token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]
