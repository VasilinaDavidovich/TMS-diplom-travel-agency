from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('current-user/', views.get_current_user, name='current-user'),
    path('delete-account/', views.delete_user_account, name='delete-account'),
    path('user-profile/', views.get_user_profile, name='user-profile'),
]