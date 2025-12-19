# ⚡ БЫСТРЫЙ ДЕПЛОЙ НА VPS

## 🚀 За 5 минут

### 1. Подключитесь к VPS
```bash
ssh root@your_vps_ip
```

### 2. Установите Docker (если нет)
```bash
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
sudo apt install docker-compose -y
```

### 3. Загрузите проект
```bash
# Вариант A: Через Git
mkdir -p /opt/bot_moderator && cd /opt/bot_moderator
git clone <ваш_репозиторий> .

# Вариант B: Через SCP (с вашего компьютера)
# scp -r * root@your_vps_ip:/opt/bot_moderator/
```

### 4. Создайте .env файл
```bash
cd /opt/bot_moderator
nano .env
```
Вставьте ваши данные (те же, что локально).

### 5. Запустите бота
```bash
mkdir -p logs
docker-compose up -d --build
```

### 6. Проверьте работу
```bash
docker-compose logs -f moderator-bot
```

## ✅ Готово!

Бот работает 24/7. Контейнер автоматически перезапускается благодаря `restart: unless-stopped` в docker-compose.yml.

## 📋 Полезные команды

```bash
# Логи
docker-compose logs -f moderator-bot

# Перезапуск
docker-compose restart moderator-bot

# Остановка
docker-compose down

# Статус
docker-compose ps
```

## 🔄 Обновление кода

```bash
cd /opt/bot_moderator
git pull  # или загрузите новые файлы
docker-compose up -d --build
```

---

**Подробная инструкция:** см. `DEPLOY_VPS.md`

