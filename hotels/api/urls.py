from django.urls import path
from . import views

urlpatterns = [
    # Отели
    path('hotels/', views.HotelListView.as_view(), name='hotel-list'),
    path('hotels/<int:pk>/', views.HotelDetailView.as_view(), name='hotel-detail-api'),

    # Отзывы
    path('reviews/', views.ReviewViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='reviews'),
    path('reviews/<int:pk>/', views.ReviewViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy'
    }), name='review-detail'),

    # Бронирования
    path('bookings/', views.BookingViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='bookings'),
    path('bookings/<int:pk>/', views.BookingViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy'
    }), name='booking-detail'),

    # Справочники
    path('countries/', views.CountryListView.as_view(), name='country-list'),
    path('cities/', views.CityListView.as_view(), name='city-list'),

    # Избранное
    path('favorites/', views.FavoriteViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='favorites'),
    path('favorites/<int:pk>/', views.FavoriteViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy'
    }), name='favorite-detail'),
]