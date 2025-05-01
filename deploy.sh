#!/bin/bash

# Остановка всех процессов, использующих порт 8000
fuser -k 8000/tcp

# Активация виртуального окружения
source .venv/bin/activate

# Обновление зависимостей
pip install -r requirements.txt

# Применение миграций
python manage.py migrate

# Сборка статических файлов
python manage.py collectstatic --noinput

# Запуск Gunicorn
gunicorn plant_shop.wsgi:application --bind 0.0.0.0:8000 --workers 4 --daemon 