from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('delete-account/', views.delete_user_account, name='delete-account'),
    path('current-user/', views.get_current_user, name='current-user'),
    path('profile/', views.profile_page, name='profile-page'),
]