from rest_framework import serializers
from core import models


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for tag object
    """
    class Meta:
        model = models.Tag
        fields = [
            'id',
            'name'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context.get("request").user
        validated_data["user"] = user
        return super().create(validated_data)


class IngredientSerializer(serializers.ModelSerializer):
    """
    Serializer for ingradients object
    """
    class Meta:
        model = models.Ingredient
        fields = [
            'id',
            'name'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context.get("request").user
        validated_data["user"] = user
        return super().create(validated_data)


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for recipe object
    """
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Tag.objects.all()
    )

    class Meta:
        model = models.Recipe
        fields = [
            'id',
            'title',
            'time_minutes',
            'price',
            'ingredients',
            'tags',
            'link'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context.get("request").user
        validated_data["user"] = user
        return super().create(validated_data)
