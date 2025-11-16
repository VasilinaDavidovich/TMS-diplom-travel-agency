from rest_framework import serializers
from django.utils import timezone
from typing import Any, Dict, Optional
from .models import Country, City, Hotel, HotelImage, Review, Booking, Favorite


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ('id', 'name')


class CitySerializer(serializers.ModelSerializer):

    country_name = serializers.CharField(
        source='country.name',
        read_only=True
    )

    class Meta:
        model = City
        fields = ('id', 'name', 'country', 'country_name')


class HotelImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = HotelImage
        fields = ('id', 'image')


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source='user.username',
        read_only=True
    )
    user_first_name = serializers.CharField(
        source='user.first_name',
        read_only=True
    )

    class Meta:
        model = Review
        fields = (
            'id',
            'hotel',
            'user',
            'user_name',
            'user_first_name',
            'rating',
            'comment',
            'created_at',
        )
        read_only_fields = ('user', 'created_at')

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Проверка, что пользователь не оставлял уже отзыв на этот отель"""
        user = self.context['request'].user
        hotel = attrs.get('hotel')

        if Review.objects.filter(user=user, hotel=hotel).exists():
            raise serializers.ValidationError(
                "Вы уже оставляли отзыв на этот отель"
            )

        return attrs


class HotelListSerializer(serializers.ModelSerializer):

    country_name = serializers.CharField(
        source='country.name',
        read_only=True
    )
    city_name = serializers.CharField(
        source='city.name',
        read_only=True
    )
    main_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = (
            'id',
            'name',
            'country_name',
            'city_name',
            'stars',
            'price_per_night',
            'main_image',
            'average_rating',
            'review_count',
        )

    def get_main_image(self, obj: Hotel) -> Optional[str]:
        first_image = obj.images.first()
        return first_image.image.url if first_image else None

    def get_average_rating(self, obj: Hotel) -> float:
        reviews = obj.reviews.all()
        return (
            sum(review.rating for review in reviews) / len(reviews)
            if reviews else 0
        )

    def get_review_count(self, obj: Hotel) -> int:
        return obj.reviews.count()


class HotelDetailSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(
        source='country.name',
        read_only=True
    )
    city_name = serializers.CharField(
        source='city.name',
        read_only=True
    )
    images = HotelImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()

    class Meta:
        model = Hotel
        fields = (
            'id',
            'name',
            'description',
            'country',
            'country_name',
            'city',
            'city_name',
            'stars',
            'address',
            'price_per_night',
            'created_at',
            'images',
            'reviews',
            'average_rating',
            'review_count'
        )


class BookingSerializer(serializers.ModelSerializer):

    hotel_name = serializers.CharField(
        source='hotel.name',
        read_only=True
    )
    user_name = serializers.CharField(
        source='user.username',
        read_only=True
    )

    class Meta:
        model = Booking
        fields = (
            'id',
            'hotel',
            'hotel_name',
            'user',
            'user_name',
            'check_in',
            'check_out',
            'guests',
            'total_price',
            'created_at'
        )
        read_only_fields = ('user', 'total_price', 'created_at')


class BookingCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = ('hotel', 'check_in', 'check_out', 'guests')

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация данных бронирования"""
        # Проверка, что дата выезда после даты заезда
        if data['check_in'] >= data['check_out']:
            raise serializers.ValidationError(
                "Дата выезда должна быть после даты заезда"
            )

        # Проверка, что дата заезда не в прошлом
        if data['check_in'] < timezone.now().date():
            raise serializers.ValidationError(
                "Нельзя бронировать на прошедшие даты"
            )

        return data


class FavoriteSerializer(serializers.ModelSerializer):
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    hotel_price = serializers.DecimalField(
        source='hotel.price_per_night',
        read_only=True,
        max_digits=10,
        decimal_places=2
    )
    hotel_city = serializers.CharField(source='hotel.city.name', read_only=True)
    hotel_country = serializers.CharField(source='hotel.country.name', read_only=True)
    hotel_image = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = (
            'id',
            'hotel',
            'hotel_name',
            'hotel_price',
            'hotel_city',
            'hotel_country',
            'hotel_image',
            'created_at'
        )
        read_only_fields = ('user', 'created_at')

    def get_hotel_image(self, obj):
        first_image = obj.hotel.images.first()
        return first_image.image.url if first_image and first_image.image else None