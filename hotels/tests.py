from django.test import TestCase
from django.contrib.auth.models import User
from .models import Country, City, Hotel
from rest_framework.test import APITestCase
from rest_framework import status

# Тест создания страны
class SimpleTest(TestCase):
    def test_country_creation(self):
        country = Country.objects.create(name="Тестовая страна")

        self.assertEqual(country.name, "Тестовая страна")
        self.assertEqual(str(country), "Тестовая страна")


# Тест создания отеля
class HotelTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Франция")
        self.city = City.objects.create(
            name="Париж",
            name_ru="Париж",
            country=self.country
        )

    def test_hotel_creation(self):
        hotel = Hotel.objects.create(
            name="Тестовый отель",
            description="Прекрасный отель в центре",
            country=self.country,
            city=self.city,
            stars=5,
            address="Улица Тестовая, 1",
            price_per_night=200.00
        )

        self.assertEqual(hotel.name, "Тестовый отель")
        self.assertEqual(hotel.stars, 5)
        self.assertEqual(hotel.price_per_night, 200.00)
        self.assertEqual(hotel.country.name, "Франция")


# Проверка API
class HotelAPITest(APITestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Италия")
        self.city = City.objects.create(
            name="Рим",
            name_ru="Рим",
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


# Тест регистрации пользователя
class AuthAPITest(APITestCase):
    def test_user_registration(self):
        registration_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

        # Отправляем POST запрос на регистрацию
        response = self.client.post('/api/auth/register/', registration_data)

        # Проверяем, что регистрация прошла успешно (статус 201)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что в ответе есть токены доступа
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        # Проверяем, что пользователь создался в базе данных
        self.assertTrue(User.objects.filter(username='testuser').exists())