from rest_framework.authtoken import views
from user import serializers
from rest_framework import generics, authentication, permissions
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


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET and PATCH user profile
    """
    serializer_class = serializers.UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
