from rest_framework import viewsets, mixins
from rest_framework import authentication
from rest_framework import permissions

from core import models

from recipe import serializers


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.TagSerializer
    queryset = models.Tag.objects.all()

    def get_queryset(self):
        """
        Return objects for authenticated user only
        """
        return self.queryset.filter(user=self.request.user).order_by("-name")


class IngradientViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.IngredientSerializer
    queryset = models.Ingredient.objects.all()

    def get_queryset(self):
        """
        Return objects for authenticated user only
        """
        return self.queryset.filter(user=self.request.user).order_by("-name")
