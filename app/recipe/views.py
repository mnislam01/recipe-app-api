from rest_framework import viewsets, mixins, status
from rest_framework import authentication
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
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

    def _str_to_int(self, string):
        return [int(item) for item in string.split(",")]

    def get_queryset(self):
        """
        Return objects for authenticated user only
        """
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")
        queryset = self.queryset

        if tags:
            queryset = queryset.filter(
                tags__id__in=self._str_to_int(tags)
            )
        if ingredients:
            queryset = queryset.filter(
                ingredients__id__in=self._str_to_int(ingredients)
            )

        return queryset.filter(user=self.request.user).order_by(
                                                        self.order_by
                                                    )

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """
        Upload an image to recipe
        """

        recipe = self.get_object()
        serializer = serializers.RecipeImageSerializer(
            recipe,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
