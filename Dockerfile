FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создаем и переходим в рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем папку для статических файлов
RUN mkdir -p /app/static
RUN mkdir -p /app/media

# Открываем порт 8000
EXPOSE 8000

# Команда для запуска сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]