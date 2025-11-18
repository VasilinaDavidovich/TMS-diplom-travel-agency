#!/bin/bash


echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database started"

echo "Applying migrations..."
python manage.py migrate contenttypes
python manage.py migrate auth
python manage.py migrate accounts
python manage.py migrate


echo "Collecting static files..."
python manage.py collectstatic --noinput


echo "Starting server..."
python manage.py runserver 0.0.0.0:8000