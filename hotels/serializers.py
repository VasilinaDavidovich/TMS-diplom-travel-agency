from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from typing import Any, Dict, Optional
from .models import Country, City, Hotel, HotelImage, Review, Booking, Favorite


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):

    country_name = serializers.CharField(
        source='country.name',
        read_only=True
    )

    class Meta:
        model = City
        fields = '__all__'


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
        fields = '__all__'


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
        fields = '__all__'
        read_only_fields = ('user', 'total_price', 'created_at')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class UserRegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'password2',
            'first_name',
            'last_name',
        )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Пароли не совпадают"
            })
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> User:
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует")
        return value


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
        return first_image.image.url if first_image else None