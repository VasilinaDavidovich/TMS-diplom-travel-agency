from rest_framework import generics, permissions, viewsets
from django.db.models import Q, Avg
from typing import Any

from ..models import Hotel, Country, City, Review, Booking, Favorite

from .serializers import (
    HotelListSerializer,
    HotelDetailSerializer,
    ReviewSerializer,
    BookingSerializer,
    CountrySerializer,
    CitySerializer,
    BookingCreateSerializer,
    FavoriteSerializer,
)

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .filters import HotelFilter

# список отелей с фильтрацией
class HotelListView(generics.ListAPIView):
    serializer_class = HotelListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = HotelFilter

    def get_queryset(self) -> Any:
        queryset = Hotel.objects.select_related('country', 'city').prefetch_related('images', 'reviews')
        return queryset
    
    def filter_queryset(self, queryset):

        # Сначала применяем фильтры (DjangoFilterBackend)
        queryset = super().filter_queryset(queryset)
        
        # Затем применяем сортировку
        ordering = self.request.query_params.get('ordering')
        sort_by = self.request.query_params.get('sort_by')
        
        # Сортировка по рейтингу (требует аннотацию)
        if sort_by == 'rating_desc':
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating')
            ).order_by('-avg_rating', 'name')
        # Сортировка по цене
        elif ordering == 'price_per_night':
            queryset = queryset.order_by('price_per_night', 'id')
        elif ordering == '-price_per_night':
            queryset = queryset.order_by('-price_per_night', 'id')
        # Сортировка по звездам
        elif ordering == 'stars':
            queryset = queryset.order_by('stars', 'id')
        elif ordering == '-stars':
            queryset = queryset.order_by('-stars', 'id')
        # Сортировка по умолчанию (если нет параметров)
        else:
            queryset = queryset.order_by('id')
        
        return queryset


# детальная страница отеля
class HotelDetailView(generics.RetrieveAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelDetailSerializer
    permission_classes = [permissions.AllowAny]


# ViewSet для отзывов
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = None  # Отключаем пагинацию для личного кабинета

    def get_queryset(self):
        # Фильтр по пользователю: /reviews/?user=username
        username = self.request.query_params.get('user')
        if username:
            return Review.objects.filter(user__username=username).select_related('hotel', 'user')

        return Review.objects.all().select_related('hotel', 'user')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ViewSet для бронирований
class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # Отключаем пагинацию для личного кабинета

    def get_queryset(self):
        # Фильтр по пользователю: /bookings/?user=username
        username = self.request.query_params.get('user')
        if username:
            return Booking.objects.filter(user__username=username).select_related('hotel', 'user')

        # По умолчанию - бронирования текущего пользователя
        return Booking.objects.filter(user=self.request.user).select_related('hotel', 'user')

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer

    def perform_create(self, serializer):
        hotel = serializer.validated_data['hotel']
        check_in = serializer.validated_data['check_in']
        check_out = serializer.validated_data['check_out']
        nights = (check_out - check_in).days
        total_price = hotel.price_per_night * nights
        serializer.save(user=self.request.user, total_price=total_price)


# список стран
class CountryListView(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


# список городов с фильтрацией
class CityListView(generics.ListAPIView):
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self) -> Any:
        queryset = City.objects.all()
        country_id = self.request.query_params.get('country')
        if country_id:
            queryset = queryset.filter(country_id=country_id)
        return queryset


# ViewSet для избранного
class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # Отключаем пагинацию для личного кабинета

    def get_queryset(self):
        # Фильтр по пользователю: /favorites/?user=username
        username = self.request.query_params.get('user')
        if username:
            return Favorite.objects.filter(user__username=username).select_related('hotel', 'user')

        # По умолчанию - избранное текущего пользователя
        return Favorite.objects.filter(user=self.request.user).select_related('hotel', 'user')

    def perform_create(self, serializer):
        hotel_id = self.request.data.get('hotel')
        hotel = Hotel.objects.get(id=hotel_id)
        if Favorite.objects.filter(user=self.request.user, hotel=hotel).exists():
            from rest_framework import serializers
            raise serializers.ValidationError("Отель уже в избранном")
        serializer.save(user=self.request.user, hotel=hotel)