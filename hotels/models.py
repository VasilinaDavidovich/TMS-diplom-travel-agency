from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from typing import List, Tuple


class Country(models.Model):

    name: models.CharField = models.CharField(
        max_length=100,
        verbose_name='Название страны'
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name: str = 'Страна'
        verbose_name_plural: str = 'Страны'
        ordering: List[str] = ['name']


class City(models.Model):
    name: models.CharField = models.CharField(
        max_length=100,
        verbose_name='Название города'
    )
    country: models.ForeignKey = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        verbose_name='Страна'
    )

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        verbose_name: str = 'Город'
        verbose_name_plural: str = 'Города'
        ordering: List[str] = ['name']

class Hotel(models.Model):

    STAR_CHOICES: List[Tuple[int, str]] = [
        (1, '⭐ (1 звезда)'),
        (2, '⭐⭐ (2 звезды)'),
        (3, '⭐⭐⭐ (3 звезды)'),
        (4, '⭐⭐⭐⭐ (4 звезды)'),
        (5, '⭐⭐⭐⭐⭐ (5 звезд)'),
    ]

    name: models.CharField = models.CharField(
        max_length=200,
        verbose_name='Название отеля'
    )
    description: models.TextField = models.TextField(
        verbose_name='Описание'
    )
    country: models.ForeignKey = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        verbose_name='Страна'
    )
    city: models.ForeignKey = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Город'
    )
    stars: models.IntegerField = models.IntegerField(
        choices=STAR_CHOICES,
        default=3,
        verbose_name='Количество звезд'
    )
    address: models.TextField = models.TextField(
        verbose_name='Адрес'
    )
    price_per_night: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за ночь (€)',
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.stars}⭐)"

    class Meta:
        verbose_name: str = 'Отель'
        verbose_name_plural: str = 'Отели'
        ordering: List[str] = ['-created_at']

    @property
    def average_rating(self) -> float:
        """Вычисляем средний рейтинг отеля"""
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0.0

    @property
    def review_count(self) -> int:
        """Количество отзывов"""
        return self.reviews.count()


class HotelImage(models.Model):

    hotel: models.ForeignKey = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Отель'
    )
    image: models.ImageField = models.ImageField(
        upload_to='hotel_images/',
        verbose_name='Изображение'
    )

    def __str__(self) -> str:
        return f"Изображение {self.hotel.name}"

    class Meta:
        verbose_name: str = 'Изображение отеля'
        verbose_name_plural: str = 'Изображения отелей'


class Review(models.Model):

    RATING_CHOICES: List[Tuple[int, int]] = [(i, i) for i in range(1, 6)]

    hotel: models.ForeignKey = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Отель'
    )
    user: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    rating: models.IntegerField = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Рейтинг'
    )
    comment: models.TextField = models.TextField(
        verbose_name='Комментарий'
    )
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def __str__(self) -> str:
        return f"Отзыв {self.user.username} на {self.hotel.name}"

    class Meta:
        verbose_name: str = 'Отзыв'
        verbose_name_plural: str = 'Отзывы'
        ordering: List[str] = ['-created_at']
        unique_together: List[str] = ['hotel', 'user']


class Booking(models.Model):

    hotel: models.ForeignKey = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        verbose_name='Отель'
    )
    user: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    check_in: models.DateField = models.DateField(
        verbose_name='Дата заезда'
    )
    check_out: models.DateField = models.DateField(
        verbose_name='Дата выезда'
    )
    guests: models.IntegerField = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Количество гостей'
    )
    total_price: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Общая стоимость'
    )
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата бронирования'
    )

    def calculate_total_price(self) -> Decimal:
        """Расчет общей стоимости бронирования"""
        nights: int = (self.check_out - self.check_in).days
        if nights <= 0:
            return Decimal('0')
        return self.hotel.price_per_night * nights

    def save(self, *args, **kwargs) -> None:
        """Автоматически рассчитывать стоимость при сохранении"""
        if not self.total_price:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Бронь {self.user.username} в {self.hotel.name}"

    class Meta:
        verbose_name: str = 'Бронирование'
        verbose_name_plural: str = 'Бронирования'
        ordering: List[str] = ['-created_at']


class Favorite(models.Model):
    user: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    hotel: models.ForeignKey = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        verbose_name='Отель'
    )
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    def __str__(self) -> str:
        return f"{self.user.username} - {self.hotel.name}"

    class Meta:
        verbose_name: str = 'Избранный отель'
        verbose_name_plural: str = 'Избранные отели'
        unique_together: List[str] = ['user', 'hotel']