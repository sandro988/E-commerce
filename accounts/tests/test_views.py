from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token


User = get_user_model()


class SignUpTests(APITestCase):
    def setUp(self):
        self.signup_url = reverse("signup_api_view")
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

        # Creating a duplicate user.
        response = self.client.post(
            self.signup_url,
            self.correct_user_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_register_user_with_incorrect_data(self):
        response = self.client.post(
            self.signup_url, self.incorrect_user_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)


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