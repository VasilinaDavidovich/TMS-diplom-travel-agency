from django.urls import path
from . import views

urlpatterns = [
    # Отели
    path('hotels/', views.HotelListView.as_view(), name='hotel-list'),
    path('hotels/<int:pk>/', views.HotelDetailView.as_view(), name='hotel-detail-api'),

    # Отзывы
    path('reviews/', views.ReviewCreateView.as_view(), name='review-create'),
    path('my-reviews/', views.UserReviewsView.as_view(), name='user-reviews'),
    path('reviews/delete/<int:review_id>/', views.delete_review, name='review-delete'),

    # Бронирования
    path('bookings/', views.BookingCreateView.as_view(), name='booking-create'),
    path('my-bookings/', views.UserBookingsView.as_view(), name='user-bookings'),

    # Справочники
    path('countries/', views.CountryListView.as_view(), name='country-list'),
    path('cities/', views.CityListView.as_view(), name='city-list'),

    # Избранное
    path('favorites/', views.FavoriteListView.as_view(), name='favorite-list'),
    path('favorites/add/', views.FavoriteCreateView.as_view(), name='favorite-add'),
    path('favorites/remove/<int:pk>/', views.FavoriteDeleteView.as_view(), name='favorite-remove'),
]