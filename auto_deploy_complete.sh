#!/bin/bash
# ПОЛНОСТЬЮ АВТОМАТИЧЕСКИЙ ДЕПЛОЙ НА VPS
# Выполнить на VPS одной командой

set -e

PROJECT_DIR="/opt/bot_moderator"
GIT_REPO="https://github.com/bocharov62-bit/bot_moderator.git"

echo "=========================================="
echo "АВТОМАТИЧЕСКИЙ ДЕПЛОЙ БОТА НА VPS"
echo "=========================================="
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функция для вывода статуса
print_status() {
    echo -e "${YELLOW}[$1]${NC} $2"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Шаг 1: Установка Docker
print_status "1/7" "Проверка и установка Docker..."
if ! command -v docker &> /dev/null; then
    echo "Установка Docker..."
    apt update -qq > /dev/null 2>&1
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh > /dev/null 2>&1
    rm get-docker.sh
    print_success "Docker установлен: $(docker --version)"
else
    print_success "Docker уже установлен: $(docker --version)"
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Установка Docker Compose..."
    apt install -y docker-compose > /dev/null 2>&1
    print_success "Docker Compose установлен: $(docker-compose --version)"
else
    print_success "Docker Compose уже установлен: $(docker-compose --version)"
fi
echo ""

# Шаг 2: Загрузка проекта
print_status "2/7" "Загрузка проекта с GitHub..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

if [ -d ".git" ]; then
    echo "Репозиторий существует, обновляем..."
    git pull > /dev/null 2>&1
    print_success "Проект обновлён"
else
    echo "Клонируем репозиторий..."
    git clone $GIT_REPO . > /dev/null 2>&1
    print_success "Проект загружен"
fi
echo ""

# Шаг 3: Создание .env
print_status "3/7" "Настройка .env файла..."
if [ ! -f .env ]; then
    cp .env.example .env
    chmod 600 .env
    
    # Автоматическое заполнение .env из переменных окружения или запрос данных
    echo ""
    echo "=========================================="
    echo "НАСТРОЙКА .ENV ФАЙЛА"
    echo "=========================================="
    echo ""
    echo "Введите данные для .env файла:"
    echo ""
    
    read -p "BOT_TOKEN: " BOT_TOKEN
    read -p "DB_HOST [31.31.197.6]: " DB_HOST
    DB_HOST=${DB_HOST:-31.31.197.6}
    read -p "DB_PORT [3306]: " DB_PORT
    DB_PORT=${DB_PORT:-3306}
    read -p "DB_USER: " DB_USER
    read -p "DB_PASSWORD: " DB_PASSWORD
    read -p "DB_NAME: " DB_NAME
    read -p "LOG_LEVEL [INFO]: " LOG_LEVEL
    LOG_LEVEL=${LOG_LEVEL:-INFO}
    
    # Запись в .env
    cat > .env << EOF
BOT_TOKEN=$BOT_TOKEN
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_NAME=$DB_NAME
DATABASE_URL=mysql+aiomysql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME
LOG_LEVEL=$LOG_LEVEL
LOG_FILE=logs/bot.log
EOF
    
    chmod 600 .env
    print_success ".env файл создан и заполнен"
else
    print_success ".env файл уже существует"
fi
echo ""

# Шаг 4: Создание директории для логов
print_status "4/7" "Создание директории для логов..."
mkdir -p logs
chmod 755 logs
print_success "Директория logs создана"
echo ""

# Шаг 5: Сборка образа
print_status "5/7" "Сборка Docker образа..."
docker-compose build > /dev/null 2>&1
print_success "Docker образ собран"
echo ""

# Шаг 6: Запуск бота
print_status "6/7" "Запуск бота..."
docker-compose up -d > /dev/null 2>&1
print_success "Бот запущен"
echo ""

# Шаг 7: Проверка
print_status "7/7" "Проверка работы..."
sleep 3

echo ""
echo "=========================================="
echo "СТАТУС КОНТЕЙНЕРА"
echo "=========================================="
docker-compose ps
echo ""

echo "=========================================="
echo "ПОСЛЕДНИЕ ЛОГИ"
echo "=========================================="
docker-compose logs --tail=30 moderator-bot
echo ""

echo "=========================================="
echo -e "${GREEN}ДЕПЛОЙ ЗАВЕРШЁН УСПЕШНО!${NC}"
echo "=========================================="
echo ""
echo "Полезные команды:"
echo "  Логи:   cd $PROJECT_DIR && docker-compose logs -f moderator-bot"
echo "  Статус: cd $PROJECT_DIR && docker-compose ps"
echo "  Стоп:   cd $PROJECT_DIR && docker-compose down"
echo "  Старт:  cd $PROJECT_DIR && docker-compose up -d"
echo ""

