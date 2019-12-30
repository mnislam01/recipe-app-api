from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import (
    get_user_model,
    authenticate
)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user model
    """

    class Meta:
        model = get_user_model()
        fields = [
            "email",
            "password",
            "name"
        ]
        extra_kwargs = {"password": {"write_only": True, "min_length": 6}}

    def create(self, validated_data):
        """
        Create a user with the an encrypted password and return the user
        """
        return get_user_model().objects.create_user(**validated_data)


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer user authentication token
    """
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': "password"},
        trim_whitespace=False
    )

    def validate(self, attr):
        email = attr.get("email")
        password = attr.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password
        )
        if not user:
            raise serializers.ValidationError(
                    _("Unable to authenticate"), code="authentication"
                )

        attr["user"] = user
        return attr
