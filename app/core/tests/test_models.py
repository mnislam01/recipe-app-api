from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """
        Test creating a user with email successfull
        """
        email = "nazrul@localmachine.com"
        password = "TestPass12345"
        user = get_user_model().objects.create_user(
                                            email=email,
                                            password=password
                                        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """
        Test the email of the user normalized
        """
        email = "nazrul@LOCALMACHINE.COM"
        user = get_user_model().objects.create_user(
                                        email=email,
                                        password="test12345"
                                    )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """
        Test creating user with no email raise error
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "test12345")

    def test_create_new_superuser(self):
        """
        Test creating a new super user
        """

        user = get_user_model().objects.create_superuser(
                                        email="nazrul@localmachine.com",
                                        password="test12345"
                                    )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
