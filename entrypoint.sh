#!/bin/bash

# Ждем пока база данных будет готова
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database started"

# Применяем миграции
echo "Applying migrations..."
# Применяем миграции в правильном порядке с обходом проблем зависимостей
python manage.py migrate auth --fake-if-needed
python manage.py migrate admin --fake-if-needed
python manage.py migrate accounts --fake-if-needed
python manage.py migrate --run-syncdb

# Загружаем фикстуры (если база пустая)
echo "Checking if database is empty..."
if python manage.py shell -c "from hotels.models import Hotel; print('Database has data' if Hotel.objects.exists() else 'Database is empty')" | grep -q "Database is empty"; then
    echo "Loading fixtures..."
    python manage.py loaddata fixtures/countries.json fixtures/cities.json fixtures/hotels.json fixtures/hotel_images.json
else
    echo "Database already has data, skipping fixtures"
fi

# Собираем статические файлы
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Запускаем сервер
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000