#!/bin/bash

# Ждем пока база данных будет готова
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database started"

echo "Applying migrations..."
# Сначала базовые миграции
python manage.py migrate contenttypes
python manage.py migrate auth
python manage.py migrate accounts
# Затем все остальные
python manage.py migrate

echo "Loading fixtures..."
python manage.py loaddata fixtures/countries.json fixtures/cities.json fixtures/hotels.json fixtures/hotel_images.json

# Собираем статические файлы
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Запускаем сервер
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000