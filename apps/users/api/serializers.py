from rest_framework import serializers
from rest_framework.validators import ValidationError
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        print(attrs)
        user = authenticate(username=attrs["email"], password=attrs["password"])

        if not user and user.is_active is not True:
            raise ValidationError("User credentials did not match")

        refresh = RefreshToken.for_user(user)

        return {"access": str(refresh.access_token), "refresh": str(refresh)}
