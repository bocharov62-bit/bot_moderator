#!/bin/bash
# Скрипт автоматического деплоя на VPS
# Использование: ./deploy.sh

set -e

echo "=========================================="
echo "ДЕПЛОЙ TELEGRAM-БОТА МОДЕРАТОРА НА VPS"
echo "=========================================="
echo ""

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker не установлен. Установите Docker сначала."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "[ERROR] Docker Compose не установлен. Установите Docker Compose сначала."
    exit 1
fi

echo "[OK] Docker установлен: $(docker --version)"
echo "[OK] Docker Compose установлен: $(docker-compose --version)"
echo ""

# Проверка .env файла
if [ ! -f .env ]; then
    echo "[WARNING] Файл .env не найден!"
    echo "Создайте файл .env с необходимыми переменными."
    exit 1
fi

echo "[OK] Файл .env найден"
echo ""

# Создание директории для логов
mkdir -p logs
echo "[OK] Директория logs создана"
echo ""

# Остановка существующих контейнеров
echo "Остановка существующих контейнеров..."
docker-compose down 2>/dev/null || true
echo "[OK] Старые контейнеры остановлены"
echo ""

# Сборка образа
echo "Сборка Docker образа..."
docker-compose build --no-cache
echo "[OK] Образ собран"
echo ""

# Запуск контейнера
echo "Запуск бота..."
docker-compose up -d
echo "[OK] Бот запущен"
echo ""

# Ожидание запуска
echo "Ожидание запуска бота (5 секунд)..."
sleep 5

# Проверка статуса
echo "Проверка статуса..."
if docker-compose ps | grep -q "Up"; then
    echo "[OK] Бот работает!"
    echo ""
    echo "Логи:"
    docker-compose logs --tail=10 moderator-bot
    echo ""
    echo "=========================================="
    echo "ДЕПЛОЙ ЗАВЕРШЁН УСПЕШНО!"
    echo "=========================================="
    echo ""
    echo "Полезные команды:"
    echo "  Просмотр логов: docker-compose logs -f moderator-bot"
    echo "  Перезапуск:     docker-compose restart moderator-bot"
    echo "  Остановка:     docker-compose down"
    echo "  Статус:        docker-compose ps"
else
    echo "[ERROR] Бот не запустился. Проверьте логи:"
    docker-compose logs moderator-bot
    exit 1
fi

