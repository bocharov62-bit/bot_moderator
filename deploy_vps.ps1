# Автоматический деплой на VPS
$VPS_IP = "31.31.197.6"
$VPS_USER = "root"
$PROJECT_DIR = "/opt/bot_moderator"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ДЕПЛОЙ НА VPS: $VPS_IP" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Шаг 1: Проверка SSH
Write-Host "[1/7] Проверка SSH..." -ForegroundColor Yellow
ssh -o ConnectTimeout=5 $VPS_USER@$VPS_IP "echo 'SSH OK'"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ОШИБКА] Не удалось подключиться" -ForegroundColor Red
    Write-Host "Выполните: ssh $VPS_USER@$VPS_IP" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] SSH работает" -ForegroundColor Green
Write-Host ""

# Шаг 2: Docker
Write-Host "[2/7] Установка Docker..." -ForegroundColor Yellow
ssh $VPS_USER@$VPS_IP "bash -c 'if ! command -v docker &> /dev/null; then apt update -qq && curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh > /dev/null 2>&1 && echo Docker installed; else echo Docker exists; fi'"
ssh $VPS_USER@$VPS_IP "bash -c 'if ! command -v docker-compose &> /dev/null; then apt install -y docker-compose > /dev/null 2>&1 && echo Docker Compose installed; else echo Docker Compose exists; fi'"
Write-Host "[OK] Docker готов" -ForegroundColor Green
Write-Host ""

# Шаг 3: Загрузка проекта
Write-Host "[3/7] Загрузка проекта..." -ForegroundColor Yellow
ssh $VPS_USER@$VPS_IP "bash -c 'mkdir -p $PROJECT_DIR && cd $PROJECT_DIR && if [ -d .git ]; then git pull; else git clone https://github.com/bocharov62-bit/bot_moderator.git .; fi'"
Write-Host "[OK] Проект загружен" -ForegroundColor Green
Write-Host ""

# Шаг 4: .env
Write-Host "[4/7] Создание .env..." -ForegroundColor Yellow
ssh $VPS_USER@$VPS_IP "bash -c 'cd $PROJECT_DIR && if [ ! -f .env ]; then cp .env.example .env && chmod 600 .env && echo .env created; else echo .env exists; fi'"
Write-Host "[OK] .env создан" -ForegroundColor Green
Write-Host "[ВАЖНО] Заполните .env на VPS!" -ForegroundColor Yellow
Write-Host "  ssh $VPS_USER@$VPS_IP" -ForegroundColor White
Write-Host "  cd $PROJECT_DIR" -ForegroundColor White
Write-Host "  nano .env" -ForegroundColor White
Write-Host ""

# Шаг 5: Логи
Write-Host "[5/7] Создание директории logs..." -ForegroundColor Yellow
ssh $VPS_USER@$VPS_IP "bash -c 'mkdir -p $PROJECT_DIR/logs && chmod 755 $PROJECT_DIR/logs'"
Write-Host "[OK] Директория logs создана" -ForegroundColor Green
Write-Host ""

# Шаг 6: Сборка
Write-Host "[6/7] Сборка образа..." -ForegroundColor Yellow
ssh $VPS_USER@$VPS_IP "bash -c 'cd $PROJECT_DIR && docker-compose build'"
Write-Host "[OK] Образ собран" -ForegroundColor Green
Write-Host ""

# Шаг 7: Запуск
Write-Host "[7/7] Запуск бота..." -ForegroundColor Yellow
ssh $VPS_USER@$VPS_IP "bash -c 'cd $PROJECT_DIR && docker-compose up -d'"
Write-Host "[OK] Бот запущен" -ForegroundColor Green
Write-Host ""

# Проверка
Write-Host "Статус:" -ForegroundColor Cyan
ssh $VPS_USER@$VPS_IP "bash -c 'cd $PROJECT_DIR && docker-compose ps'"
Write-Host ""

Write-Host "Логи:" -ForegroundColor Cyan
ssh $VPS_USER@$VPS_IP "bash -c 'cd $PROJECT_DIR && docker-compose logs --tail=20 moderator-bot'"
Write-Host ""

Write-Host "==========================================" -ForegroundColor Green
Write-Host "ДЕПЛОЙ ЗАВЕРШЁН!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

