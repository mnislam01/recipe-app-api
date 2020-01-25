import tempfile
import os
from PIL import Image
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse("recipe:recipe-list")


def image_upload_url(recipe_id):
    """
    return url for recipe iamge upload
    """
    return reverse("recipe:recipe-upload-image", args=[recipe_id])


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


def sample_tag(user, **params):
    """
    Creates a smaple tag object
    """
    defaults = {
        "name": "Sample Tag"
    }
    defaults.update(params)

    return Tag.objects.create(user=user, **defaults)


def sample_ingredient(user, **params):
    """
    Creates a smaple ingredient object
    """
    defaults = {
        "name": "Sample ingredient"
    }
    defaults.update(params)

    return Ingredient.objects.create(user=user, **defaults)


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


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """
        Test uploading an image to recipe
        """
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)

            res = self.client.post(url, {"image": ntf}, format="multipart")

            self.recipe.refresh_from_db()

            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn('image', res.data)
            self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """
        """
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {"image": "NoImage"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipies_by_tags(self):
        """
        Test filtering recipies by tags
        """
        recipe1 = sample_recipe(user=self.user, title="Thai vegetable curry")
        recipe2 = sample_recipe(user=self.user, title="Auvergine with tahini")
        tag1 = sample_tag(user=self.user, name="vegan")
        tag2 = sample_tag(user=self.user, name="vegetarian")
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)

        res = self.client.get(
            RECIPE_URL,
            {"tags": f"{tag1.id}, {tag2.id}"}
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_filter_recipies_by_ingredients(self):
        """
        Test filtering recipies by Ingrediants
        """
        recipe1 = sample_recipe(user=self.user, title="Posh beans on toast")
        recipe2 = sample_recipe(user=self.user, title="Chicken Cachiatore")
        ingr1 = sample_ingredient(user=self.user, name="Feta cheese")
        ingr2 = sample_ingredient(user=self.user, name="Chicken")
        recipe1.ingredients.add(ingr1)
        recipe2.ingredients.add(ingr2)

        res = self.client.get(
            RECIPE_URL,
            {"ingredients": f"{ingr1.id}, {ingr2.id}"}
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
