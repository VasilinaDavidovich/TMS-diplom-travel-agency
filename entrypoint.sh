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

# Собираем статические файлы
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Запускаем сервер
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000