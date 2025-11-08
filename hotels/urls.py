from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from .views import (
    HotelListView,
    HotelDetailView,
    ReviewCreateView,
    BookingCreateView,
    UserBookingsView,
    CountryListView,
    CityListView,
    home_page,
    hotel_detail_page,
    search_results_page,
)

urlpatterns = [
    # Аутентификация
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', views.get_user_profile, name='profile'),

    # Frontend страницы
    path('', home_page, name='home'),
    path('hotel/<int:hotel_id>/', hotel_detail_page, name='hotel-detail-page'),
    path('search/', search_results_page, name='search-results'),

    # Отели
    path('hotels/', HotelListView.as_view(), name='hotel-list'),
    path('hotels/<int:pk>/', HotelDetailView.as_view(), name='hotel-detail-api'),

    # Отзывы
    path('reviews/', ReviewCreateView.as_view(), name='review-create'),

    # Бронирования
    path('bookings/', BookingCreateView.as_view(), name='booking-create'),
    path('my-bookings/', UserBookingsView.as_view(), name='user-bookings'),

    # Справочники
    path('countries/', CountryListView.as_view(), name='country-list'),
    path('cities/', CityListView.as_view(), name='city-list'),
]