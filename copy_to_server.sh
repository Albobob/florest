#!/bin/bash

# Копирование файлов на сервер
scp -i C:\Users\trebl\.ssh\id_rsa -r ./* root@185.236.23.116:/var/www/plant_shop/

# Копирование скриптов на сервер
scp -i C:\Users\trebl\.ssh\id_rsa deploy.sh root@185.236.23.116:/var/www/plant_shop/
scp -i C:\Users\trebl\.ssh\id_rsa setup_server.sh root@185.236.23.116:/var/www/plant_shop/

# Установка прав на скрипты
ssh -i C:\Users\trebl\.ssh\id_rsa root@185.236.23.116 "chmod +x /var/www/plant_shop/deploy.sh"
ssh -i C:\Users\trebl\.ssh\id_rsa root@185.236.23.116 "chmod +x /var/www/plant_shop/setup_server.sh" 