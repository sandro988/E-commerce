from django.contrib.auth import get_user_model
from django.test import TestCase
from django.db.utils import IntegrityError


class AccountsManagerTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            email="test_user@email.com", password="test_pass"
        )

        self.assertEqual(user.email, "test_user@email.com")
        self.assertTrue(user.check_password("test_pass"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_verified)
        # Checking that user object has no username.
        self.assertFalse(hasattr(user, "username"))
        # Checking that the password is hashed
        self.assertNotEqual(user.password, "test_pass")

    def test_create_user_with_invalid_email(self):
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="test_pass")

    def test_create_users_with_duplicate_email(self):
        User = get_user_model()
        User.objects.create_user(email="test_user@email.com", password="test_pass")

        with self.assertRaises(IntegrityError):
            User.objects.create_user(email="test_user@email.com", password="test_pass")

    def test_create_superuser(self):
        User = get_user_model()
        super_user = User.objects.create_superuser(
            email="test_super_user@email.com", password="test_super_pass"
        )

        self.assertEqual(super_user.email, "test_super_user@email.com")
        self.assertTrue(super_user.check_password("test_super_pass"))
        self.assertTrue(super_user.is_active)
        self.assertTrue(super_user.is_staff)
        self.assertTrue(super_user.is_superuser)
        self.assertTrue(super_user.is_verified)
        # Checking that user object has no username.
        self.assertFalse(hasattr(super_user, "username"))
        # Checking that the password is hashed
        self.assertNotEqual(super_user.password, "test_pass")

    def test_create_superuser_with_false_attributes(self):
        super_user = get_user_model()

        # Checking that an error occures when creating superuser and
        # is_superuser or is_staff attributes are set to False.

        with self.assertRaises(ValueError):
            super_user.objects.create_superuser(
                email="test_superuser1@email.com",
                password="test_super_pass",
                is_superuser=False,
            )

        with self.assertRaises(ValueError):
            super_user.objects.create_superuser(
                email="test_superuser1@email.com",
                password="test_super_pass",
                is_staff=False,
            )
