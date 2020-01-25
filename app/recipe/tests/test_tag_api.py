from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer
from .test_recipe_api import sample_tag, sample_recipe


TAGS_URL = reverse("recipe:tag-list")


def sample_user(email="nazrul@localmachine.com", password="TestPass12345"):
    return get_user_model().objects.create_user(email, password)


class PublicTagsApiTest(TestCase):
    """
    Test the publicly available Tags api
    """
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
        Test that login is required for retrieving Tags
        """
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    """
    Test the authorize user tags api
    """
    def setUp(self):
        self.user = sample_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """
        Test retrieving Tags
        """
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """
        Test that tags are for authenticated user
        """
        user2 = sample_user(email="test@localmachine.com")
        Tag.objects.create(user=user2, name="Fruity")
        tag = Tag.objects.create(user=self.user, name="Meaty")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0].get("name"), tag.name)

    def test_tags_create_successful(self):
        """
        Test creating a new tag
        """
        payload = {
            "name": "Test Tag"
        }
        res = self.client.post(TAGS_URL, payload)
        tags = Tag.objects.filter(
            user=self.user,
            **payload
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(tags.exists())

    def test_tags_create_invalid(self):
        """
        Test creating a invalid payload
        """
        payload = {
            "name": ""
        }
        res = self.client.post(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """
        Test tags are retrieved for recipies
        """
        tag1 = sample_tag(user=self.user, name="Breakfast")
        tag2 = sample_tag(user=self.user, name="Lunch")
        recipe = sample_recipe(
            user=self.user,
            title="Coriander eggs on toast",
            price=5.00,
            time_minutes=10
        )
        recipe.tags.add(tag1)

        res = self.client.get(
            TAGS_URL,
            {"assigned_only": 1}
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
