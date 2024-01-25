from dj_rest_auth.views import LoginView, LogoutView
from django.urls import path
from .views import (
    SignUpAPIView,
    OTPVerificationView,
    CustomLogoutView,
    CustomUserDetailsView,
    ResendVerificationCodeView,
)


urlpatterns = [
    path("login/", LoginView.as_view(), name="login_api_view"),
    path("logout/", CustomLogoutView.as_view(http_method_names=['post']), name="logout_api_view"),
    path("signup/", SignUpAPIView.as_view(), name="signup_api_view"),
    path("verification/", OTPVerificationView.as_view(), name="verification_api_view"),
    path(
        "verification/resend/",
        ResendVerificationCodeView.as_view(),
        name="verification_resend_api_view",
    ),
    path("user/", CustomUserDetailsView.as_view(), name="user_details_api_view"),
]
