from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
PROFILE_URL = reverse("user:profile")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUsersApiTest(TestCase):
    """
    Tests the users API (PUBLIC)
    """
    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """
        Test creating user with valid payload is successful
        """
        payload = {
            "email": "nazrul@localmachine.com",
            "password": "test12345",
            "name": "Test User"
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        password = payload.pop("password")
        user = get_user_model().objects.get(**payload)
        self.assertTrue(user.check_password(password))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """
        Test creating a user already exists fails
        """
        payload = {
            "email": "nazrul@localmachine.com",
            "password": "test12345",
            "name": "Test User"
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """
        """
        payload = {
            "email": "nazrul@localmachine.com",
            "password": "test",
            "name": "Test User"
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(**{
                                        "email": "nazrul@localmachine.com",
                                        "name": "Test User"
                                    }
                                ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user_success(self):
        """
        Test a token is created for the user
        """
        payload = {
            "email": "nazrul@localmachine.com",
            "password": "test12345",
            "name": "Test User"
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_invalid_credentials_fails(self):
        """
        Test token not created in credentials is invalid
        """
        payload = {
            "email": "nazrul@localmachine.com",
            "password": "test12345",
            "name": "Test User"
        }
        create_user(**payload)
        payload["password"] = "test54321"
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_no_user(self):
        """
        Test token is not created is user does not exists
        """
        payload = {
            "email": "nazrul@localmachine.com",
            "password": "test12345",
            "name": "Test User"
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_missing_field(self):
        """
        Test that email and password are required
        """
        payload = {
            "email": "",
            "password": "",
            "name": "Test User"
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_retrieve_user_unauthorized(self):
        """
        Test authentication is required for user
        """
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user_unauthorized(self):
        """
        Test authentication is required for user
        """
        res = self.client.delete(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """
    Test api requests that require authentication
    """

    def setUp(self):
        self.user = create_user(**{
                "email": "nazrul@localmachine.com",
                "password": "test12345",
                "name": "Test User"
            }
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """
        """
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
                "name": self.user.name,
                "email": self.user.email
            }
        )

    def test_post_method_not_allowed_to_retrieve_url(self):
        """
        """
        res = self.client.post(PROFILE_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile_success(self):
        """
        """
        payload = {
                "email": "nazrul@localmachine.com",
                "password": "test54321",  # Changed
                "name": "Test User"
            }

        res = self.client.patch(PROFILE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload["name"])
        self.assertEqual(self.user.email, payload["email"])
        self.assertTrue(self.user.check_password(payload["password"]))

    def test_delete_user_profile_success(self):
        """
        """
        res = self.client.delete(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        user_found = get_user_model().objects.filter(**{
                    "email": "nazrul@localmachine.com",
                    "name": "Test User"
                }
            )
        self.assertEqual(user_found.count(), 0)
