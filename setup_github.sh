#!/bin/bash

# Установка Git
apt-get update
apt-get install -y git

# Создание директории для проекта
mkdir -p /var/www/plant_shop
cd /var/www/plant_shop

# Клонирование репозитория
git clone https://github.com/Albobob/florest.git .

# Создание виртуального окружения
python3 -m venv .venv
source .venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Настройка прав доступа
chown -R www-data:www-data /var/www/plant_shop
chmod -R 755 /var/www/plant_shop 