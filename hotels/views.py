from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q, Avg
from django.shortcuts import render, get_object_or_404
from typing import Any, Dict

from .models import Hotel, Country, City, Review, Booking, Favorite
from .serializers import (
    UserSerializer,
    HotelListSerializer,
    HotelDetailSerializer,
    ReviewSerializer,
    BookingSerializer,
    CountrySerializer,
    CitySerializer,
    UserRegisterSerializer,
    BookingCreateSerializer,
    FavoriteSerializer,
)


# регистрация пользователя
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


# получение профиля юзера
@api_view(['GET'])
def get_user_profile(request) -> Response:
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# список отелей с фильтрацией
class HotelListView(generics.ListAPIView):
    serializer_class = HotelListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self) -> Any:
        queryset = Hotel.objects.all()

        # фильтр по странам
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country_id=country)

        # фильтр по городам
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city_id=city)

        # фильтр по количеству звезд
        stars = self.request.query_params.get('stars')
        if stars:
            queryset = queryset.filter(stars=stars)

        # фильтр по стоимости
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)

        # поиск по названию и городу
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(city__name__iexact=search)
            )
            print(f"Результатов после поиска: {queryset.count()}")

        # СОРТИРОВКА
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

    def perform_create(self, serializer: ReviewSerializer) -> None:
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


# главная страница
def home_page(request) -> Any:
    # Выводится 6 рандомных отелей из базы данных
    hotels = Hotel.objects.all().order_by('?')[:6]
    context: Dict[str, Any] = {'hotels': hotels}
    return render(request, 'home.html', context)


# страница конкретного отеля
def hotel_detail_page(request, hotel_id: int) -> Any:
    hotel = get_object_or_404(Hotel, id=hotel_id)
    context: Dict[str, Any] = {'hotel': hotel}
    return render(request, 'hotel_detail.html', context)

# страница результатов поиска
def search_results_page(request) -> Any:
    return render(request, 'search_results.html')

# профиль юзера
def profile_page(request):
    return render(request, 'profile.html')

# удаление аккаунта
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_user_account(request):
    user = request.user
    user.delete()
    return Response(
        {"message": "Аккаунт успешно удален"},
        status=status.HTTP_200_OK
    )

# Для получения данных пользователя (вывод в личном кабинете)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_current_user(request):
    """API для получения данных текущего пользователя."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


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

        # Проверяем нет ли уже в избранном
        if Favorite.objects.filter(user=self.request.user, hotel=hotel).exists():
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
    """Список отзывов текущего пользователя"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).select_related('hotel')

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_review(request, review_id):
    """Удаление отзыва пользователем"""
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