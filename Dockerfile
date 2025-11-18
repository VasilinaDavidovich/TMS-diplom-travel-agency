FROM python:3.13-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создаем и переходим в рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости (добавили netcat-openbsd для проверки БД)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем весь проект
COPY . .

# Даем права на выполнение entrypoint.sh
RUN chmod +x entrypoint.sh

# Создаем папки для статических файлов и медиа
RUN mkdir -p /app/static
RUN mkdir -p /app/media

# Открываем порт 8000
EXPOSE 8000

# Запускаем entrypoint через bash
ENTRYPOINT ["/bin/bash", "entrypoint.sh"]