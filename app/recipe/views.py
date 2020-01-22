from rest_framework import viewsets, mixins
from rest_framework import authentication
from rest_framework import permissions

from core import models

from recipe import serializers


class BaseGenericViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.CreateModelMixin):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    order_by = "-name"

    def get_queryset(self):
        """
        Return objects for authenticated user only
        """
        return self.queryset.filter(user=self.request.user).order_by(
                                                        self.order_by
                                                    )


class TagViewSet(BaseGenericViewSet):

    serializer_class = serializers.TagSerializer
    queryset = models.Tag.objects.all()


class IngradientViewSet(BaseGenericViewSet):

    serializer_class = serializers.IngredientSerializer
    queryset = models.Ingredient.objects.all()


class RecipeViewSet(BaseGenericViewSet):

    serializer_class = serializers.RecipeSerializer
    queryset = models.Recipe.objects.all()
    order_by = "-id"
