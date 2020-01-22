from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer


RECIPE_URL = reverse("recipe:recipe-list")


def sample_user(email="nazrul@localmachine.com", password="TestPass12345"):
    """
    Create a sample user
    """
    return get_user_model().objects.create_user(email, password)


def sample_recipe(user, **params):
    """
    Creates a smaple recipe object
    """
    defaults = {
        "title": "Sample Recipe",
        "time_minutes": 10,
        "price": 5.00,
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTest(TestCase):
    """
    Test the publicly available recipe api
    """
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
        Test that login is required for retrieving recipes
        """
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PriveRecipeApiTest(TestCase):
    """
    Test the authorize user recipe api
    """
    def setUp(self):
        self.user = sample_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipies(self):
        """
        Test retrieving Recipies
        """
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipies = Recipe.objects.all().order_by("-id")
        serializer = RecipeSerializer(recipies, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipies_limited_to_user(self):
        """
        Test that recipies are for authenticated user
        """
        user2 = sample_user(email="test@localmachine.com")
        sample_recipe(user=user2)
        recipe = sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0].get("title"), recipe.title)

    def test_recipe_create_successful(self):
        """
        Test creating a new recipe
        """
        payload = {
            "title": "Egg Kichodi",
            "time_minutes": 120,
            "price": 5
        }
        res = self.client.post(RECIPE_URL, payload)
        recipe = Recipe.objects.filter(
            user=self.user,
            **payload
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(recipe.exists())

    def test_recipie_create_invalid(self):
        """
        Test creating recipe with invalid payload
        """
        payload = {
            "title": ""
        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
