from django.contrib.auth import get_user_model
from .models import Country, City, Hotel
from rest_framework.test import APITestCase
from rest_framework import status

from datetime import date, timedelta
from .models import Booking

User = get_user_model()


# Проверка API
class HotelAPITest(APITestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Италия")
        self.city = City.objects.create(
            name="Рим",
            country=self.country
        )
        self.hotel = Hotel.objects.create(
            name="Римский отель",
            description="Отель в историческом центре",
            country=self.country,
            city=self.city,
            stars=4,
            address="Площадь Тестовая, 1",
            price_per_night=150.00
        )

    def test_hotel_list_api(self):
        response = self.client.get('/api/hotels/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(len(response.data) > 0)

        first_hotel = response.data[0]
        self.assertEqual(first_hotel['name'], "Римский отель")


# Тесты валидации бронирования
class BookingValidationTest(APITestCase):
    def setUp(self):
        # Создаем пользователя
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

        # Создаем данные для отеля
        self.country = Country.objects.create(name="Франция")
        self.city = City.objects.create(
            name="Париж",
            country=self.country
        )
        self.hotel = Hotel.objects.create(
            name="Парижский отель",
            description="Отель в центре Парижа",
            country=self.country,
            city=self.city,
            stars=5,
            address="Улица Тестовая, 1",
            price_per_night=200.00
        )

        # Авторизуем пользователя
        self.client.force_authenticate(user=self.user)

        # Даты для тестов
        self.tomorrow = date.today() + timedelta(days=1)
        self.day_after_tomorrow = date.today() + timedelta(days=2)
        self.yesterday = date.today() - timedelta(days=1)

    def test_booking_success(self):
        """успешное создание бронирования"""
        data = {
            'hotel': self.hotel.id,
            'check_in': self.tomorrow.strftime('%Y-%m-%d'),
            'check_out': self.day_after_tomorrow.strftime('%Y-%m-%d'),
            'guests': 2
        }
        response = self.client.post('/api/bookings/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)

        booking = Booking.objects.first()
        self.assertEqual(booking.hotel, self.hotel)
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.guests, 2)
        # Проверка расчета стоимости: 200.00 * 1 ночь = 200.00
        self.assertEqual(float(booking.total_price), 200.00)

    def test_booking_checkout_before_checkin(self):
        """дата выезда должна быть после даты заезда"""
        data = {
            'hotel': self.hotel.id,
            'check_in': self.day_after_tomorrow.strftime('%Y-%m-%d'),
            'check_out': self.tomorrow.strftime('%Y-%m-%d'),
            'guests': 1
        }
        response = self.client.post('/api/bookings/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Дата выезда должна быть после даты заезда', str(response.data))

    def test_booking_checkout_equal_checkin(self):
        """дата выезда не может быть равна дате заезда"""
        data = {
            'hotel': self.hotel.id,
            'check_in': self.tomorrow.strftime('%Y-%m-%d'),
            'check_out': self.tomorrow.strftime('%Y-%m-%d'),
            'guests': 1
        }
        response = self.client.post('/api/bookings/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Дата выезда должна быть после даты заезда', str(response.data))

    def test_booking_past_date(self):
        """нельзя бронировать на прошедшие даты"""
        data = {
            'hotel': self.hotel.id,
            'check_in': self.yesterday.strftime('%Y-%m-%d'),
            'check_out': self.tomorrow.strftime('%Y-%m-%d'),
            'guests': 1
        }
        response = self.client.post('/api/bookings/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Нельзя бронировать на прошедшие даты', str(response.data))