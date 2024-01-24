from django.contrib.auth import get_user_model
from rest_framework import serializers
from dj_rest_auth.serializers import (
    LoginSerializer,
    UserDetailsSerializer,
)


User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
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


class CustomLoginSerializer(LoginSerializer):
    """
    Overriding LoginSerializer from dj_rest_auth package so that
    there is no need for users to input username when they want to sign in.
    """

    username = None


class CustomUserDetailsSerializer(UserDetailsSerializer):
    """
    Overriding UserDetailsSerializer from dj_rest_auth package so that
    there are more fields included from the CustomUser model in the swagger docs.
    """

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
        )