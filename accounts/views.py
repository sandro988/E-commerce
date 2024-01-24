from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from accounts.serializers import SignUpSerializer
from dj_rest_auth.views import UserDetailsView


class SignUpAPIView(CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [
        AllowAny,
    ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            {"message": "Successfully created a new user."},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class CustomUserDetailsView(UserDetailsView):
    parser_classes = (JSONParser, MultiPartParser)
