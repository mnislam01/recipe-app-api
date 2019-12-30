from rest_framework.authtoken import views
from user import serializers
from rest_framework import generics
from rest_framework.settings import api_settings


class CreateUserView(generics.CreateAPIView):
    """
    Create a new user in the system
    """
    serializer_class = serializers.UserSerializer


class CreateTokenView(views.ObtainAuthToken):
    """
    Create a new auth token
    """
    serializer_class = serializers.AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
