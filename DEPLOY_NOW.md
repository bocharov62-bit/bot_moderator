# 🚀 БЫСТРЫЙ ДЕПЛОЙ НА VPS 31.31.197.6

## Автоматический деплой одной командой

### Вариант 1: Выполнить скрипт на VPS

1. Подключитесь к VPS:
```bash
ssh root@31.31.197.6
```

2. Загрузите и выполните скрипт:
```bash
# Загрузить скрипт
curl -o deploy_on_vps.sh https://raw.githubusercontent.com/bocharov62-bit/bot_moderator/main/deploy_on_vps.sh

# Или создать вручную (скопировать содержимое deploy_on_vps.sh)

# Выполнить
bash deploy_on_vps.sh
```

### Вариант 2: Пошаговое выполнение

Выполните команды на VPS по порядку:

```bash
# 1. Подключение
ssh root@31.31.197.6

# 2. Установка Docker
apt update && apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
apt install docker-compose -y

# 3. Загрузка проекта
mkdir -p /opt/bot_moderator
cd /opt/bot_moderator
git clone https://github.com/bocharov62-bit/bot_moderator.git .

# 4. Создание .env
cp .env.example .env
nano .env
# Вставьте ваши данные и сохраните (Ctrl+O, Enter, Ctrl+X)
chmod 600 .env

# 5. Запуск
mkdir -p logs
docker-compose up -d --build

# 6. Проверка
docker-compose logs -f moderator-bot
```

## ✅ Готово!

Бот работает 24/7 на VPS!

