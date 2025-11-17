from rest_framework import serializers
from ..models import CustomUser
from django.contrib.auth.password_validation import validate_password
from typing import Any, Dict


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'password',
            'password2',
            'first_name',
            'last_name',
        )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Пароли не совпадают"
            })
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> CustomUser:
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует")
        return value