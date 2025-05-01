#!/bin/bash

# Обновление системы
apt-get update
apt-get upgrade -y

# Установка необходимых пакетов
apt-get install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib

# Создание пользователя для приложения
useradd -m -s /bin/bash plant_shop
usermod -aG sudo plant_shop

# Создание директории для проекта
mkdir -p /var/www/plant_shop
chown plant_shop:plant_shop /var/www/plant_shop

# Настройка PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE plant_shop;"
sudo -u postgres psql -c "CREATE USER plant_shop WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE plant_shop TO plant_shop;"

# Настройка Nginx
cat > /etc/nginx/sites-available/plant_shop << EOF
server {
    listen 80;
    server_name 185.236.23.116;

    location /static/ {
        alias /var/www/plant_shop/static/;
    }

    location /media/ {
        alias /var/www/plant_shop/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Активация конфигурации Nginx
ln -s /etc/nginx/sites-available/plant_shop /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# Настройка брандмауэра
ufw allow 80
ufw allow 22
ufw enable 