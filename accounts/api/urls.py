from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('current-user/', views.get_current_user, name='current-user'),
    path('delete-account/', views.delete_user_account, name='delete-account'),
    path('user-profile/', views.get_user_profile, name='user-profile'),
]