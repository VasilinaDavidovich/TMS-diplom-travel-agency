from rest_framework import generics, permissions, status
from django.db.models import Q, Avg
from typing import Any
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from ..models import Hotel, Country, City, Review, Booking, Favorite

from ..serializers import (
    HotelListSerializer,
    HotelDetailSerializer,
    ReviewSerializer,
    BookingSerializer,
    CountrySerializer,
    CitySerializer,
    BookingCreateSerializer,
    FavoriteSerializer,
)


# список отелей с фильтрацией
class HotelListView(generics.ListAPIView):
    serializer_class = HotelListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self) -> Any:
        queryset = Hotel.objects.all()

        # Фильтр по странам
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country_id=country)

        # Фильтр по городам
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city_id=city)

        # Фильтр по количеству звезд
        stars = self.request.query_params.get('stars')
        if stars:
            queryset = queryset.filter(stars=stars)

        # Фильтр по стоимости
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)

        # Поиск по названию и городу
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(city__name__iexact=search)
            )

        # Сортировка
        sort_by = self.request.query_params.get('sort_by')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price_per_night')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price_per_night')
        elif sort_by == 'stars_asc':
            queryset = queryset.order_by('stars')
        elif sort_by == 'stars_desc':
            queryset = queryset.order_by('-stars')
        elif sort_by == 'rating_desc':
            queryset = queryset.annotate(
                avg_rating=Avg('reviews__rating')
            ).order_by('-avg_rating', 'name')

        return queryset


# детальная страница отеля
class HotelDetailView(generics.RetrieveAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelDetailSerializer
    permission_classes = [permissions.AllowAny]


# создание отзыва
class ReviewCreateView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# создание бронирования
class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        hotel = serializer.validated_data['hotel']
        check_in = serializer.validated_data['check_in']
        check_out = serializer.validated_data['check_out']
        nights = (check_out - check_in).days
        total_price = hotel.price_per_night * nights
        serializer.save(user=self.request.user, total_price=total_price)


# список бронирований пользователя
class UserBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related('hotel')


# список стран
class CountryListView(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [permissions.AllowAny]


# список городов с фильтрацией
class CityListView(generics.ListAPIView):
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self) -> Any:
        queryset = City.objects.all()
        country_id = self.request.query_params.get('country')
        if country_id:
            queryset = queryset.filter(country_id=country_id)
        return queryset


# Список избранных отелей (для личного кабинета)
class FavoriteListView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('hotel')


# Добавить отель в избранное
class FavoriteCreateView(generics.CreateAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        hotel_id = self.request.data.get('hotel')
        hotel = Hotel.objects.get(id=hotel_id)
        if Favorite.objects.filter(user=self.request.user, hotel=hotel).exists():
            from rest_framework import serializers
            raise serializers.ValidationError("Отель уже в избранном")
        serializer.save(user=self.request.user, hotel=hotel)


# Удалить из избранного
class FavoriteDeleteView(generics.DestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)


# Список отзывов пользователя
class UserReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).select_related('hotel')


# Удаление отзыва
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_review(request, review_id):
    try:
        review = Review.objects.get(id=review_id, user=request.user)
        review.delete()
        return Response(
            {"message": "Отзыв успешно удален"},
            status=status.HTTP_200_OK
        )
    except Review.DoesNotExist:
        return Response(
            {"error": "Отзыв не найден или у вас нет прав для его удаления"},
            status=status.HTTP_404_NOT_FOUND
        )