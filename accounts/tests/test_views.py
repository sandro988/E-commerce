from datetime import timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core import mail
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from accounts.models import OTP
from accounts.tasks import delete_expired_otps

User = get_user_model()


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class SignUpTests(APITestCase):
    def setUp(self):
        self.signup_url = reverse("signup_api_view")
        self.verification_url = reverse("verification_api_view")
        self.verification_resend_url = reverse("verification_resend_api_view")

        self.correct_user_data = {
            "email": "test_user@email.com",
            "password": "test_pass",
        }
        self.incorrect_user_data = {
            "email": "test_user@email.com",
            "password": "",
        }

    def test_register_user(self):
        response = self.client.post(
            self.signup_url,
            self.correct_user_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().email, "test_user@email.com")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject, "One time code for account verification."
        )
        self.assertEqual(
            mail.outbox[0].to,
            [
                "test_user@email.com",
            ],
        )

        # Creating a duplicate user.
        response = self.client.post(
            self.signup_url,
            self.correct_user_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_register_user_with_incorrect_data(self):
        response = self.client.post(
            self.signup_url, self.incorrect_user_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_user_verification(self):
        signup_response = self.client.post(
            self.signup_url,
            self.correct_user_data,
            format="json",
        )
        self.assertEqual(signup_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        otp_from_email = mail.outbox[0].body
        self.assertEqual(OTP.objects.count(), 1)
        self.assertEqual(OTP.objects.first().code, otp_from_email)

        verification_data = {
            "email": mail.outbox[0].to[0],
            "otp_code": mail.outbox[0].body,
        }

        verification_response = self.client.post(
            self.verification_url,
            verification_data,
            format="json",
        )
        self.assertEqual(verification_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            verification_response.data,
            {"message": "User successfully verified."},
        )
        self.assertTrue(User.objects.first().is_verified)
        self.assertIsNone(
            OTP.objects.first()
        )  # OTP gets deleted upon successful verification from db.

        verification_response = self.client.post(
            self.verification_url,
            verification_data,
            format="json",
        )  # Trying to verify an already verified user.
        self.assertEqual(verification_response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            verification_response.data,
            {
                "message": "User is already verified, you can not reverify an already verified user."
            },
        )

    def test_user_verification_with_incorrect_data(self):
        signup_response = self.client.post(
            self.signup_url,
            self.correct_user_data,
            format="json",
        )
        self.assertEqual(signup_response.status_code, status.HTTP_201_CREATED)

        verification_response = self.client.post(
            self.verification_url,
            {
                "email": "incorrect_data@email.com",
                "otp_code": "######",
            },
            format="json",
        )
        self.assertEqual(verification_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(verification_response.data, {"message": "User not found."})
        self.assertEqual(
            OTP.objects.count(), 1
        )  # OTP should not be deleted when verification fails.

        verification_response = self.client.post(
            self.verification_url,
            {
                "email": mail.outbox[0].to[0],
                "otp_code": "######",
            },
            format="json",
        )
        self.assertEqual(verification_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(verification_response.data, {"message": "Invalid OTP code."})
        self.assertEqual(OTP.objects.count(), 1)

    def test_resend_verification(self):
        signup_response = self.client.post(
            self.signup_url,
            self.correct_user_data,
            format="json",
        )
        self.assertEqual(signup_response.status_code, status.HTTP_201_CREATED)
        previous_otp = OTP.objects.last()

        response = self.client.post(
            self.verification_resend_url,
            {"email": mail.outbox[0].to[0]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {"message": "Verification code resent successfully."},
        )
        current_otp = OTP.objects.last()
        self.assertNotEqual(previous_otp.code, current_otp.code)
        self.assertEqual(
            OTP.objects.count(), 1
        )  # When resending the verification code, the previous one gets updated so we do not save two or more otp codes for the user in a database.

        verification_response = self.client.post(
            self.verification_url,
            {
                "email": mail.outbox[0].to[0],
                "otp_code": mail.outbox[1].body,
            },
            format="json",
        )

        self.assertEqual(verification_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            verification_response.data,
            {"message": "User successfully verified."},
        )
        self.assertEqual(OTP.objects.count(), 0)
        self.assertTrue(User.objects.first().is_verified)

        resend_verification_response = self.client.post(
            self.verification_resend_url,
            {"email": mail.outbox[0].to[0]},
            format="json",
        )  # Resending verification code for an user who is already verified

        self.assertEqual(
            resend_verification_response.status_code, status.HTTP_409_CONFLICT
        )
        self.assertEqual(
            resend_verification_response.data,
            {"message": "User is already verified."},
        )
        self.assertEqual(OTP.objects.count(), 0)

    def test_resend_verification_with_incorrect_data(self):
        signup_response = self.client.post(
            self.signup_url,
            self.correct_user_data,
            format="json",
        )
        self.assertEqual(signup_response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(
            self.verification_resend_url,
            {
                "email": "incorrect_data@email.com",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {"message": "User not found."},
        )

    def test_verification_code_expired(self):
        self.client.post(
            self.signup_url,
            self.correct_user_data,
            format="json",
        )

        verification_code = OTP.objects.last()
        verification_code.expiry_timestamp = timezone.now() - timedelta(days=1)
        verification_code.save()
        delete_expired_otps()  # Calling periodic task for deleting expired OTP's.

        verification_data = {
            "email": mail.outbox[0].to[0],
            "otp_code": mail.outbox[0].body,
        }

        verification_response = self.client.post(
            self.verification_url,
            verification_data,
            format="json",
        )

        self.assertEqual(verification_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.last().is_verified)
        self.assertIsNone(OTP.objects.last())


class AuthenticationTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="test_user@email.com",
            password="test_pass",
            full_name="John Doe",
            phone_number="+1-202-555-0142",
            birthdate="1998-08-18",
            address="United States, Florida, Opa-locka, 3990 NW 132nd St",
            preferred_currency="USD",
            is_verified=True,  # User will be verified so that I do not have to rewrite tests about verification process which have already been tested in SignUpTests class.
        )

    def setUp(self):
        self.login_url = reverse("login_api_view")
        self.logout_url = reverse("logout_api_view")

        self.correct_user_data = {
            "email": "test_user@email.com",
            "password": "test_pass",
        }
        self.incorrect_user_data = {
            "email": "test_user@email.com",
            "password": "incorrect_test_pass",
        }

    def test_login_user(self):
        login_response = self.client.post(
            self.login_url,
            self.correct_user_data,
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("key", login_response.data)
        token_exists = Token.objects.filter(user=self.user).exists()
        self.assertTrue(
            token_exists, "Authentication token should be created for verified user."
        )

        # Authenticated user should be able to access user page where they will see their account information.
        token_key = login_response.data.get("key")
        headers = {"Authorization": f"Token {token_key}"}
        self.assertEqual(
            self.client.get(
                reverse("user_details_api_view"),
                format="json",
                headers=headers,
            ).status_code,
            status.HTTP_200_OK,
        )

    def test_login_user_with_incorrect_data(self):
        login_response = self.client.post(
            self.login_url,
            self.incorrect_user_data,
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_400_BAD_REQUEST)
        token_exists = Token.objects.filter(user=self.user).exists()
        self.assertFalse(
            token_exists,
            "Authentication token should not be created for unverified user.",
        )

    def test_login_unverified_user(self):
        self.user.is_verified = False
        self.user.save()

        login_response = self.client.post(
            self.login_url,
            self.correct_user_data,
            format="json",
        )

        self.assertEqual(login_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("key", login_response.data)
        token_exists = Token.objects.filter(user=self.user).exists()
        self.assertFalse(
            token_exists,
            "Authentication token should not be created for unverified user.",
        )

    def test_logout_user(self):
        login_response = self.client.post(
            self.login_url, self.correct_user_data, format="json"
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        token_key = login_response.data.get("key")
        self.assertIsNotNone(token_key, "Authentication token key should be present.")

        # Including the token in the headers for the logout request
        headers = {"Authorization": f"Token {token_key}"}
        logout_response = self.client.post(
            self.logout_url,
            headers=headers,
        )

        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", logout_response.data)
        self.assertEqual(logout_response.data.get("detail"), "Successfully logged out.")
        self.assertEqual(
            self.client.get(
                reverse("user_details_api_view"),
                format="json",
            ).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        # logging out after we have already logged out
        logout_response = self.client.post(self.logout_url)
        self.assertEqual(
            logout_response.data.get("detail"), "You are already logged out."
        )


class UserDetailViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="test_user@email.com",
            password="test_pass",
            full_name="John Doe",
            phone_number="+1-202-555-0142",
            birthdate="1998-08-18",
            address="United States, Florida, Opa-locka, 3990 NW 132nd St",
            preferred_currency="USD",
        )
        cls.token = Token.objects.create(user=cls.user)

        cls.put_request_data = {
            "full_name": "Maia Koelpin IV",
            "phone_number": "+1-202-555-0110",
            "birthdate": "1977-08-28",
            "address": "United States, New Jersey, Newton, 82 Pond St",
            "profile_image": None,
            "preferred_currency": "USD",
            "is_subscribed_to_newsletter": True,
        }
        cls.patch_request_data = {
            "full_name": "Maia Koelpin IV",
            "preferred_currency": "GEL",
            "is_subscribed_to_newsletter": True,
        }

    def setUp(self) -> None:
        self.url = reverse("user_details_api_view")
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_user_details_on_get_request(self):
        response = self.client.get(
            self.url,
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        # Extracting user data from the request anc checking that they are correct.
        user_data = response.data
        self.assertEqual(user_data["email"], self.user.email)
        self.assertEqual(user_data["full_name"], self.user.full_name)
        self.assertEqual(user_data["phone_number"], self.user.phone_number)
        self.assertEqual(user_data["birthdate"], str(self.user.birthdate))
        self.assertEqual(user_data["address"], self.user.address)
        self.assertEqual(user_data["profile_image"], None)
        self.assertEqual(user_data["preferred_currency"], self.user.preferred_currency)
        self.assertEqual(user_data["is_subscribed_to_newsletter"], False)
        self.assertEqual(user_data["is_verified"], False)

    def test_user_details_on_put_request(self):
        response = self.client.put(
            self.url,
            self.put_request_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Extracting user data from the request anc checking that they are correct.
        user_data = response.data
        self.assertEqual(user_data["full_name"], "Maia Koelpin IV")
        self.assertEqual(
            user_data["phone_number"], "+12025550110"
        )  # in database phone numbers are saved without dashes.
        self.assertEqual(user_data["birthdate"], "1977-08-28")
        self.assertEqual(
            user_data["address"], "United States, New Jersey, Newton, 82 Pond St"
        )
        self.assertEqual(user_data["profile_image"], None)
        self.assertEqual(user_data["preferred_currency"], "USD")
        self.assertEqual(user_data["is_subscribed_to_newsletter"], True)

    def test_user_details_on_patch_request(self):
        response = self.client.patch(
            self.url,
            self.patch_request_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Extracting user data from the request anc checking that they are correct.
        user_data = response.data
        self.assertEqual(user_data["full_name"], "Maia Koelpin IV")
        self.assertEqual(user_data["preferred_currency"], "GEL")
        self.assertEqual(user_data["is_subscribed_to_newsletter"], True)

    def test_user_details_with_unauthenticated_user(self):
        # Unsetind the credentials for a client by calling the credentials() method without passing any arguments.
        self.client.credentials()

        response = self.client.put(
            self.url,
            self.put_request_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(
            User.objects.last().full_name, self.put_request_data["full_name"]
        )

        response = self.client.patch(
            self.url,
            self.patch_request_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(
            User.objects.last().full_name, self.put_request_data["full_name"]
        )


class PasswordChangeTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="test_user@email.com",
            password="test_pass",
            full_name="John Doe",
            phone_number="+1-202-555-0142",
            birthdate="1998-08-18",
            address="United States, Florida, Opa-locka, 3990 NW 132nd St",
            preferred_currency="USD",
            is_verified=True,
        )

    def setUp(self) -> None:
        user_data = {
            "email": "test_user@email.com",
            "password": "test_pass",
        }
        self.password_change_data = {
            "old_password": "test_pass",
            "new_password1": "new_password_123",
            "new_password2": "new_password_123",
        }

        self.password_change_url = reverse("password_change_api_view")
        self.login_url = reverse("login_api_view")
        self.client = APIClient()

        # First signing user in
        login_response = self.client.post(
            self.login_url,
            user_data,
            format="json",
        )
        token_key = login_response.data.get("key")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token_key}")

    def test_password_change_view(self):
        response = self.client.post(
            self.password_change_url,
            self.password_change_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data.get("detail"), "New password has been saved.")
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertTrue(updated_user.check_password("new_password_123"))

    def test_password_change_with_incorrect_old_password(self):
        self.password_change_data["old_password"] = "incorrect_old_password"
        response = self.client.post(
            self.password_change_url,
            self.password_change_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Password should not change.
        user = User.objects.get(pk=self.user.pk)
        self.assertFalse(user.check_password("new_password_123"))
        self.assertTrue(user.check_password("test_pass"))

    def test_password_change_with_non_matching_new_passwords(self):
        self.password_change_data["new_password2"] = "new_password_123456789"
        response = self.client.post(
            self.password_change_url,
            self.password_change_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Password should not change.
        user = User.objects.get(pk=self.user.pk)
        self.assertFalse(user.check_password("new_password_123"))
        self.assertFalse(user.check_password("new_password_123456789"))
        self.assertTrue(user.check_password("test_pass"))

    def test_password_change_with_unauthenticated_user(self):
        self.client.post(reverse("logout_api_view"))
        response = self.client.post(
            self.password_change_url,
            self.password_change_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Password should not change.
        user = User.objects.get(pk=self.user.pk)
        self.assertFalse(user.check_password("new_password_123"))
        self.assertTrue(user.check_password("test_pass"))


class PasswordResetTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="test_user@email.com",
            password="test_pass",
            full_name="John Doe",
            phone_number="+1-202-555-0142",
            birthdate="1998-08-18",
            address="United States, Florida, Opa-locka, 3990 NW 132nd St",
            preferred_currency="USD",
            is_verified=True,
        )

    def setUp(self) -> None:
        self.password_reset_url = reverse("password_reset_api_view")
        self.client = APIClient()

    def send_password_reset_request(self, email):
        """
        Helper method to send a password reset request and extract reset URL.
        Returns (uidb64, token) tuple.
        """

        password_reset_url = reverse("password_reset_api_view")
        reset_data = {"email": email}
        self.client.post(password_reset_url, reset_data, format="json")

        # Getting reset confirm URL
        email_body = mail.outbox[0].body
        start_index = email_body.find("Reset URL: ")
        end_index = email_body.find("\n", start_index)
        reset_confirm_url = email_body[start_index:end_index].split(": ")[1]

        # Extracting uidb64 and token from reset confirm URL
        uidb64, token = reset_confirm_url.split("/")[7:9]

        return uidb64, token

    def test_password_reset(self):
        reset_response = self.client.post(
            self.password_reset_url,
            {"email": "test_user@email.com"},
            format="json",
        )

        self.assertEqual(reset_response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", reset_response.data)
        self.assertEqual(
            reset_response.data.get("detail"), "Password reset e-mail has been sent."
        )
        self.assertEqual(
            len(mail.outbox), 1
        )  # Checking that mail has been sent to user.

    def test_password_reset_with_non_existing_email(self):
        reset_response = self.client.post(
            self.password_reset_url,
            {"email": "email_that_does_not_exist@email.com"},
            format="json",
        )

        self.assertEqual(reset_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            len(mail.outbox), 0
        )  # Checking that mail has not been sent to user.

    def test_password_reset_with_invalid_email_format(self):
        reset_response = self.client.post(
            self.password_reset_url,
            {"email": "invalid_email_format"},
            format="json",
        )

        self.assertEqual(reset_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("detail", reset_response.data)
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_confirm_view(self):
        # All the necessary data
        uidb64, token = self.send_password_reset_request("test_user@email.com")
        confirm_url = reverse(
            "password_reset_confirm", kwargs={"uidb64": uidb64, "token": token}
        )
        confirm_data = {
            "new_password1": "new_password_123",
            "new_password2": "new_password_123",
            "uid": uidb64,
            "token": token,
        }

        # Request
        reset_confirm_response = self.client.post(
            confirm_url, confirm_data, format="json"
        )

        self.assertEqual(reset_confirm_response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", reset_confirm_response.data)
        self.assertEqual(
            reset_confirm_response.data.get("detail"),
            "Password has been reset with the new password.",
        )
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertTrue(updated_user.check_password("new_password_123"))

    def test_password_reset_confirm_view_with_invalid_uidb64(self):
        # All the necessary data
        uidb64, token = self.send_password_reset_request("test_user@email.com")
        uidb64 = "invalid uidb64"
        confirm_url = reverse(
            "password_reset_confirm", kwargs={"uidb64": uidb64, "token": token}
        )
        confirm_data = {
            "new_password1": "new_password_123",
            "new_password2": "new_password_123",
            "uid": uidb64,
            "token": token,
        }

        # Request
        reset_confirm_response = self.client.post(
            confirm_url, confirm_data, format="json"
        )

        self.assertEqual(
            reset_confirm_response.status_code, status.HTTP_400_BAD_REQUEST
        )
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertFalse(updated_user.check_password("new_password_123"))

    def test_password_reset_confirm_view_with_invalid_token(self):
        # All the necessary data
        uidb64, token = self.send_password_reset_request("test_user@email.com")
        token = "invalid token"
        confirm_url = reverse(
            "password_reset_confirm", kwargs={"uidb64": uidb64, "token": token}
        )
        confirm_data = {
            "new_password1": "new_password_123",
            "new_password2": "new_password_123",
            "uid": uidb64,
            "token": token,
        }

        # Request
        reset_confirm_response = self.client.post(
            confirm_url, confirm_data, format="json"
        )

        self.assertEqual(
            reset_confirm_response.status_code, status.HTTP_400_BAD_REQUEST
        )
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertFalse(updated_user.check_password("new_password_123"))

    def test_password_reset_confirm_view_with_non_matching_passwords(self):
        # All the necessary data
        uidb64, token = self.send_password_reset_request("test_user@email.com")
        confirm_url = reverse(
            "password_reset_confirm", kwargs={"uidb64": uidb64, "token": token}
        )
        confirm_data = {
            "new_password1": "new_password_123",
            "new_password2": "new_password_123456789",
            "uid": uidb64,
            "token": token,
        }

        # Request
        reset_confirm_response = self.client.post(
            confirm_url, confirm_data, format="json"
        )

        self.assertEqual(
            reset_confirm_response.status_code, status.HTTP_400_BAD_REQUEST
        )
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertFalse(updated_user.check_password("new_password_123"))
        self.assertFalse(updated_user.check_password("new_password_123456789"))
        self.assertTrue(
            updated_user.check_password("test_pass")
        )  # Password of the user that I created in setUpTestData

    def test_password_reset_confirm_view_with_invalid_password(self):
        # All the necessary data
        uidb64, token = self.send_password_reset_request("test_user@email.com")
        confirm_url = reverse(
            "password_reset_confirm", kwargs={"uidb64": uidb64, "token": token}
        )
        confirm_data = {
            "new_password1": "AB3",  # This password should not be valid because it is too short
            "new_password2": "AB3",
            "uid": uidb64,
            "token": token,
        }

        # Request
        reset_confirm_response = self.client.post(
            confirm_url, confirm_data, format="json"
        )

        self.assertEqual(
            reset_confirm_response.status_code, status.HTTP_400_BAD_REQUEST
        )
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertFalse(updated_user.check_password("AB3"))
        self.assertTrue(updated_user.check_password("test_pass"))

    def test_password_reset_confirm_view_with_empty_password(self):
        # All the necessary data
        uidb64, token = self.send_password_reset_request("test_user@email.com")
        confirm_url = reverse(
            "password_reset_confirm", kwargs={"uidb64": uidb64, "token": token}
        )
        confirm_data = {
            "new_password1": "",
            "new_password2": "",
            "uid": uidb64,
            "token": token,
        }

        # Request
        reset_confirm_response = self.client.post(
            confirm_url, confirm_data, format="json"
        )

        self.assertEqual(
            reset_confirm_response.status_code, status.HTTP_400_BAD_REQUEST
        )
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertFalse(updated_user.check_password(""))
