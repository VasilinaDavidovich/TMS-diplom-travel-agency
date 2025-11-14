from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.shortcuts import render
from typing import Any, Dict

from .serializers import UserSerializer, UserRegisterSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request) -> Response:
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_user_profile(request) -> Response:
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_user_account(request):
    user = request.user
    user.delete()
    return Response(
        {"message": "Аккаунт успешно удален"},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_current_user(request):
    """API для получения данных текущего пользователя"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


def profile_page(request):
    """Frontend страница личного кабинета"""
    return render(request, 'profile.html')