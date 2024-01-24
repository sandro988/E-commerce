from dj_rest_auth.views import LoginView, LogoutView
from django.urls import path
from .views import SignUpAPIView, CustomUserDetailsView


urlpatterns = [
    path("signup/", SignUpAPIView.as_view(), name="signup_api_view"),
    path("login/", LoginView.as_view(), name="login_api_view"),
    path("logout/", LogoutView.as_view(), name="logout_api_view"),
    path("user/", CustomUserDetailsView.as_view(), name="user_details_api_view"),
]
