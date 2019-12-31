from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGRADIENTS_URL = reverse('recipe:ingredient-list')


def sample_user(email="nazrul@localmachine.com", password="TestPass12345"):
    return get_user_model().objects.create_user(email, password)


class PublicIngradientsApiTest(TestCase):
    """
    Test that Indradients api publicly unavailable
    """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
        Test that login is required for retrieving Indradients
        """
        res = self.client.get(INGRADIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngradientsApiTest(TestCase):
    """
    Test the authorize user Indradients api
    """
    def setUp(self):
        self.user = sample_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_indradients(self):
        """
        Test retrieving Indradients
        """
        Ingredient.objects.create(user=self.user, name="Milk")
        Ingredient.objects.create(user=self.user, name="Suger")

        res = self.client.get(INGRADIENTS_URL)
        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """
        Test that ingredients are for authenticated user
        """
        user2 = sample_user(email="test@localmachine.com")
        Ingredient.objects.create(user=user2, name="Suger")
        ingredient = Ingredient.objects.create(user=self.user, name="Milk")

        res = self.client.get(INGRADIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0].get("name"), ingredient.name)

    def test_ingredients_create_successful(self):
        """
        Test creating a new ingredients
        """
        payload = {
            "name": "Potato"
        }
        res = self.client.post(INGRADIENTS_URL, payload)
        ingredients = Ingredient.objects.filter(
            user=self.user,
            **payload
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ingredients.exists())

    def test_ingredients_create_invalid(self):
        """
        Test creating ingredients with invalid payload
        """
        payload = {
            "user": self.user,
            "name": ""
        }
        res = self.client.post(INGRADIENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
