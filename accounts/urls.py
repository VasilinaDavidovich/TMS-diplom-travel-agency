from django.urls import path
from . import views

urlpatterns = [
    # Frontend страница (возвращает HTML)
    path('profile/', views.profile_page, name='profile-page'),

    # Остальные API endpoints теперь в accounts/api/urls.py
]