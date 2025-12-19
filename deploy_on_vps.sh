#!/bin/bash
# Автоматический деплой на VPS
# Выполнить на VPS: bash <(curl -s https://raw.githubusercontent.com/bocharov62-bit/bot_moderator/main/deploy_on_vps.sh)
# Или: загрузить файл на VPS и выполнить: bash deploy_on_vps.sh

set -e

VPS_IP="31.31.197.6"
PROJECT_DIR="/opt/bot_moderator"
GIT_REPO="https://github.com/bocharov62-bit/bot_moderator.git"

echo "=========================================="
echo "АВТОМАТИЧЕСКИЙ ДЕПЛОЙ НА VPS"
echo "=========================================="
echo ""

# Шаг 1: Установка Docker
echo "[1/6] Проверка и установка Docker..."
if ! command -v docker &> /dev/null; then
    echo "Установка Docker..."
    apt update -qq
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh > /dev/null 2>&1
    echo "Docker установлен: $(docker --version)"
else
    echo "Docker уже установлен: $(docker --version)"
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Установка Docker Compose..."
    apt install -y docker-compose > /dev/null 2>&1
    echo "Docker Compose установлен: $(docker-compose --version)"
else
    echo "Docker Compose уже установлен: $(docker-compose --version)"
fi
echo "[OK] Docker готов"
echo ""

# Шаг 2: Загрузка проекта
echo "[2/6] Загрузка проекта..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

if [ -d ".git" ]; then
    echo "Репозиторий существует, обновляем..."
    git pull
else
    echo "Клонируем репозиторий..."
    git clone $GIT_REPO .
fi
echo "[OK] Проект загружен"
echo ""

# Шаг 3: Создание .env
echo "[3/6] Создание .env файла..."
if [ ! -f .env ]; then
    cp .env.example .env
    chmod 600 .env
    echo "[OK] .env файл создан из шаблона"
    echo ""
    echo "=========================================="
    echo "ВАЖНО: Заполните .env файл!"
    echo "=========================================="
    echo "Выполните: nano .env"
    echo "Вставьте ваши данные (BOT_TOKEN, DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)"
    echo ""
    read -p "Нажмите Enter после заполнения .env файла..."
else
    echo "[OK] .env файл уже существует"
fi
echo ""

# Шаг 4: Создание директории для логов
echo "[4/6] Создание директории для логов..."
mkdir -p logs
chmod 755 logs
echo "[OK] Директория logs создана"
echo ""

# Шаг 5: Сборка образа
echo "[5/6] Сборка Docker образа..."
docker-compose build
echo "[OK] Образ собран"
echo ""

# Шаг 6: Запуск бота
echo "[6/6] Запуск бота..."
docker-compose up -d
echo "[OK] Бот запущен"
echo ""

# Проверка
echo "=========================================="
echo "ПРОВЕРКА СТАТУСА"
echo "=========================================="
docker-compose ps
echo ""

echo "Последние строки логов:"
docker-compose logs --tail=20 moderator-bot
echo ""

echo "=========================================="
echo "ДЕПЛОЙ ЗАВЕРШЁН!"
echo "=========================================="
echo ""
echo "Полезные команды:"
echo "  Логи:   docker-compose logs -f moderator-bot"
echo "  Статус: docker-compose ps"
echo "  Стоп:   docker-compose down"
echo "  Старт:  docker-compose up -d"
echo ""

