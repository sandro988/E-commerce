from drf_spectacular.openapi import OpenApiExample


def retrieve_user_examples():
    """
    Provides examples for retrieving user.

    Returns:
        List[OpenApiExample]: A list of response examples for retrieving user.

    Example Usage:
        @extend_schema(examples=retrieve_user_examples())
        def get(self, request, *args, **kwargs):
            pass
    """

    return [
        OpenApiExample(
            "Valid example 1 (GET Response)",
            summary="Successfully retrieving user account",
            description="This example demonstrates the response after successfully retrieving user account.",
            value={
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "email": "user@example.com",
                "full_name": "Name Surname",
                "phone_number": "+995599123456",
                "birthdate": "2024-02-07",
                "address": "Some address",
                "profile_image": None,
                "preferred_currency": "GEL",
                "is_subscribed_to_newsletter": True,
                "is_verified": True,
            },
            response_only=True,
            status_codes=[200],
        ),
        OpenApiExample(
            "Valid example 2 (GET Response)",
            summary="Retrieving user account with unauthenticated user",
            description="This example demonstrates the response after retrieving user account while unauthenticated.",
            value={"detail": "Authentication credentials were not provided."},
            response_only=True,
            status_codes=[401],
        ),
        OpenApiExample(
            "Valid example 3 (GET Response)",
            summary="Retrieving user account with invalid token",
            description="This example demonstrates the response after retrieving user account with invalid token.",
            value={"detail": "Invalid token."},
            response_only=True,
            status_codes=[401],
        ),
    ]


def update_user_account_examples():
    """
    Provides examples for updating user account.

    Returns:
        List[OpenApiExample]: A list of request/response examples for updating user accounts with `PUT` request.

    Example Usage:
        @extend_schema(examples=update_user_account_examples())
        def put(self, request, *args, **kwargs):
            pass
    """

    return [
        OpenApiExample(
            "Valid example (PUT Request)",
            summary="Update user account with valid data(1)",
            description="Example of updating user account with valid data.",
            value={
                "email": "user@example.com",
                "full_name": "Name Surname",
                "phone_number": "599-123-456",
                "birthdate": "2024-02-07",
                "address": "Some address",
                "profile_image": None,
                "preferred_currency": "GEL",
                "is_subscribed_to_newsletter": True,
            },
            request_only=True,
        ),
        OpenApiExample(
            "Valid example 1 (PUT Request)",
            summary="Update user account with valid data(2)",
            description="Example of updating user account with valid data.",
            value={
                "email": "user@example.com",
                "full_name": "Name Surname",
                "phone_number": "+995599123456",
                "birthdate": "2024-02-07",
                "address": "Some address",
                "profile_image": None,
                "preferred_currency": "USD",
                "is_subscribed_to_newsletter": True,
            },
            request_only=True,
        ),
        OpenApiExample(
            "Valid example 2 (PUT Response)",
            summary="Update user account response",
            description="Example of response after successfully updating a user account.",
            value={
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "email": "user@example.com",
                "full_name": "Name Surname",
                "phone_number": "+995599123456",
                "birthdate": "2024-02-07",
                "address": "Some address",
                "profile_image": None,
                "preferred_currency": "GEL",
                "is_subscribed_to_newsletter": True,
                "is_verified": True,
            },
            response_only=True,
            status_codes=[200],
        ),
        OpenApiExample(
            "Valid example 3 (PUT Request)",
            summary="Update user account with invalid data",
            description="Example of updating user account with invalid data.",
            value={
                "email": "user!example.com",
                "full_name": "Name Surname",
                "phone_number": "0 11 222 3333",
                "birthdate": "2024-02-07-09",  # Format should be YYYY-MM-DD
                "address": "Some address",
                "profile_image": "String instead of file/iamge",
                "preferred_currency": "Not a GEL, USD, EUR",
                "is_subscribed_to_newsletter": "String instead of boolean",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Valid example 4 (PUT Response)",
            summary="Update user account with invalid data",
            description="This response demonstrates different kind of errors you can get if the data is invalid.",
            value={
                "email": ["Enter a valid email address."],
                "full_name": ["Ensure this field has no more than 128 characters."],
                "phone_number": ["Enter a valid phone number."],
                "birthdate": [
                    "Date has wrong format. Use one of these formats instead: YYYY-MM-DD."
                ],
                "address": ["Not a valid string."],
                "profile_image": [
                    "The submitted data was not a file. Check the encoding type on the form."
                ],
                "preferred_currency": ['"GBP" is not a valid choice.'],
                "is_subscribed_to_newsletter": ["Must be a valid boolean."],
            },
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 5 (PUT Response)",
            summary="Update user account with read_only fields",
            description="The response for a scenario when user tried to update account's verification status.",
            value={"error": "This field is read-only."},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 6 (PUT Response)",
            summary="Update user with missing fields",
            description="The response for a scenario when user tried to update account without required fields.",
            value={
                "email": ["This field is required."],
                "phone_number": ["This field is required."],
            },
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 7 (PUT Response)",
            summary="Updating with an email that belongs to other user",
            description="Example of response for updating a user account with an email that belongs to another user.",
            value={"email": ["custom user with this email already exists."]},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 8 (PUT Response)",
            summary="Update user account with empty data",
            description="If user submits empty data they will get 400 Bad Request status code.",
            value={
                "email": ["This field is required."],
                "other fields that can not be left blank": ["..."],
            },
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 9 (PUT Response)",
            summary="Updating user account with unauthenticated user",
            description="This example demonstrates the response after trying to update an user account while unauthenticated.",
            value={"detail": "Authentication credentials were not provided."},
            response_only=True,
            status_codes=[401],
        ),
        OpenApiExample(
            "Valid example 10 (PUT Response)",
            summary="Updating user account with invalid token",
            description="This example demonstrates the response after trying to update an user account with invalid token.",
            value={"detail": "Invalid token."},
            response_only=True,
            status_codes=[401],
        ),
    ]


def partial_update_user_account_examples():
    """
    Provides examples for partially updating user account.

    Returns:
        List[OpenApiExample]: A list of request/response examples for partially updating user accounts with `PATCH` request.

    Example Usage:
        @extend_schema(examples=partial_update_user_account_examples())
        def patch(self, request, *args, **kwargs):
            pass
    """

    return [
        OpenApiExample(
            "Valid example (PATCH Request)",
            summary="Partially update user account with valid data(1)",
            description="Example of partially updating user account with valid data.",
            value={
                "email": "user@example.com",
                "full_name": "Name Surname",
                "phone_number": "599-123-456",
                "birthdate": "2024-02-07",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Valid example 1 (PATCH Request)",
            summary="Partially update user account with valid data(2)",
            description="Example of partially updating user account with valid data.",
            value={
                "is_subscribed_to_newsletter": True,
            },
            request_only=True,
        ),
        OpenApiExample(
            "Valid example 2 (PATCH Request)",
            summary="Partially update user account with invalid data",
            description="Example of partially updating user account with invalid data.",
            value={
                "email": "user!example.com",
                "phone_number": "11 222 333 4444",
                "birthdate": "2024-02-07-09",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Valid example 3 (PATCH Response)",
            summary="Success response",
            description="Response after partially updating user account with valid data.",
            value={
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "email": "user@example.com",
                "full_name": "Name Surname",
                "phone_number": "+995599123456",
                "birthdate": "2024-02-07",
                "address": "Some address",
                "profile_image": None,
                "preferred_currency": "GEL",
                "is_subscribed_to_newsletter": True,
                "is_verified": True,
            },
            response_only=True,
            status_codes=[200],
        ),
        OpenApiExample(
            "Valid example 4 (PATCH Response)",
            summary="Partially update user account with invalid data",
            description="This response demonstrates different kind of errors you can get if the data is invalid.",
            value={
                "email": ["Enter a valid email address."],
                "full_name": ["Ensure this field has no more than 128 characters."],
                "phone_number": ["Enter a valid phone number."],
                "birthdate": [
                    "Date has wrong format. Use one of these formats instead: YYYY-MM-DD."
                ],
                "address": ["Not a valid string."],
                "profile_image": [
                    "The submitted data was not a file. Check the encoding type on the form."
                ],
                "preferred_currency": ['"GBP" is not a valid choice.'],
                "is_subscribed_to_newsletter": ["Must be a valid boolean."],
            },
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 5 (PATCH Response)",
            summary="Partially update user account with read_only fields",
            description="The response for a scenario when user tried to update account's verification status.",
            value={"error": "This field is read-only."},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 6 (PATCH Response)",
            summary="Partially updating with an email that belongs to other user",
            description="Example of response for partially updating a user account with an email that belongs to another user.",
            value={"email": ["custom user with this email already exists."]},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 7 (PATCH Response)",
            summary="Partially updating user account with unauthenticated user",
            description="This example demonstrates the response after trying to update an user account while unauthenticated.",
            value={"detail": "Authentication credentials were not provided."},
            response_only=True,
            status_codes=[401],
        ),
        OpenApiExample(
            "Valid example 8 (PATCH Response)",
            summary="Partially updating user account with invalid token",
            description="This example demonstrates the response after trying to update an user account with invalid token.",
            value={"detail": "Invalid token."},
            response_only=True,
            status_codes=[401],
        ),
    ]


def user_signup_examples():
    """
    Provides examples for user signup.

    Returns:
        List[OpenApiExample]: A list of response examples for user signup.

    Example Usage:
        @extend_schema(examples=user_signup_examples())
        class SignUpAPIView(CreateAPIView):
            pass
    """

    return [
        OpenApiExample(
            "Valid example 1 (POST Request)",
            summary="Create user",
            description="This example demonstrates the request with correct data for creating user.",
            value={"email": "user@example.com", "password": "strong_password123!"},
            request_only=True,
        ),
        OpenApiExample(
            "Valid example 2 (POST Request)",
            summary="Create user with invalid data(1)",
            description="This example demonstrates the request with password that is less than 8 characters for creating user.",
            value={"email": "user@example.com", "password": "short"},
            request_only=True,
        ),
        OpenApiExample(
            "Valid example 3 (POST Request)",
            summary="Create user with invalid data(2)",
            description="This example demonstrates the request with invalid email for creating user.",
            value={"email": "invalid_email.com", "password": "strong_password123!"},
            request_only=True,
        ),
        OpenApiExample(
            "Valid example 4 (POST Request)",
            summary="Create user with invalid data(3)",
            description="This example demonstrates the request with only numeric password.",
            value={"email": "invalid_email.com", "password": "1234567890"},
            request_only=True,
        ),
        OpenApiExample(
            "Valid example 5 (POST Request)",
            summary="Create user with invalid data(4)",
            description="This example demonstrates the request with missing email of password field.",
            value={"email": "invalid_email.com"},
            request_only=True,
        ),
        OpenApiExample(
            "Valid example 6 (POST Response)",
            summary="Create user",
            description="This example demonstrates the response for successfully creating user.",
            value={
                "message": "Successfully created a new user. One time code has been sent to your email, use it to verify your account."
            },
            response_only=True,
            status_codes=[201],
        ),
        OpenApiExample(
            "Valid example 7 (POST Response)",
            summary="Create user with duplicate email",
            description="This example demonstrates the response for creating user with an already existing email.",
            value={"email": ["custom user with this email already exists."]},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 8 (POST Response)",
            summary="Create user with invalid email",
            description="This example demonstrates the response for creating user with an invalid email.",
            value={"email": ["Enter a valid email address."]},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 9 (POST Response)",
            summary="Create user with short password",
            description="This example demonstrates the response for creating user with a password that is less than 8 characters.",
            value={
                "password": [
                    "This password is too short. It must contain at least 8 characters."
                ]
            },
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 10 (POST Response)",
            summary="Create user with too common password",
            description="This example demonstrates the response for creating user with a password that is too common. (e.g. 'password').",
            value={"password": ["This password is too common."]},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 11 (POST Response)",
            summary="Create user with entirely numeric password",
            description="This example demonstrates the response for creating user with a password that has only numeric values.",
            value={"password": ["This password is entirely numeric."]},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 12 (POST Response)",
            summary="Create user with missing fields",
            description="This example demonstrates the response for creating user with a missing **password**.",
            value={"password": ["This field is required."]},
            response_only=True,
            status_codes=[400],
        ),
        OpenApiExample(
            "Valid example 13 (POST Response)",
            summary="Create user while authenticated",
            description="This example demonstrates the response for creating user while being authenticated. only the **unauthenticated** \
                should be allowed to create new accounts.",
            value={"detail": "You do not have permission to perform this action."},
            response_only=True,
            status_codes=[403],
        ),
    ]
