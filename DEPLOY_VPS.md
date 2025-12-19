# 🚀 РУКОВОДСТВО ПО ДЕПЛОЮ НА VPS

## 📋 Подготовка проекта

### 1. Структура файлов для деплоя

Убедитесь, что у вас есть все необходимые файлы:
- `Dockerfile`
- `docker-compose.yml`
- `requirements.txt`
- `.env` (не коммитится, создаётся на сервере)
- `bot/` - директория с кодом
- `init.sql` - SQL скрипт для создания таблиц

### 2. Файлы для загрузки на VPS

Создайте архив проекта (исключая .env и логи):
```bash
# На Windows (PowerShell)
Compress-Archive -Path bot, docker-compose.yml, Dockerfile, requirements.txt, init.sql, README.md -DestinationPath bot_moderator.zip -Force
```

Или используйте Git для клонирования на сервере.

---

## 🖥️ Настройка VPS

### Требования к VPS:
- **ОС**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **RAM**: минимум 512 MB (рекомендуется 1 GB+)
- **Диск**: минимум 5 GB
- **Процессор**: 1 ядро (достаточно)

### Шаг 1: Подключение к VPS

```bash
ssh root@your_vps_ip
# или
ssh username@your_vps_ip
```

### Шаг 2: Обновление системы

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### Шаг 3: Установка Docker

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Проверка установки
docker --version
docker-compose --version
```

Если `docker-compose` не установлен:
```bash
sudo apt install docker-compose -y
# или
sudo pip3 install docker-compose
```

### Шаг 4: Создание директории проекта

```bash
mkdir -p /opt/bot_moderator
cd /opt/bot_moderator
```

---

## 📦 Загрузка проекта на VPS

### Вариант 1: Через Git (рекомендуется)

```bash
# Установка Git (если нет)
sudo apt install git -y

# Клонирование репозитория
git clone <ваш_репозиторий> /opt/bot_moderator
cd /opt/bot_moderator
```

### Вариант 2: Через SCP (с локального компьютера)

```bash
# На вашем компьютере (Windows PowerShell)
scp -r bot docker-compose.yml Dockerfile requirements.txt init.sql README.md root@your_vps_ip:/opt/bot_moderator/
```

### Вариант 3: Через архив

```bash
# На вашем компьютере - создайте архив
# Затем на VPS:
cd /opt/bot_moderator
# Загрузите архив через SCP или веб-интерфейс
unzip bot_moderator.zip
```

---

## ⚙️ Настройка на VPS

### Шаг 1: Создание файла .env

```bash
cd /opt/bot_moderator
nano .env
```

Вставьте содержимое (те же данные, что и локально):
```env
BOT_TOKEN=your_telegram_bot_token_here
DB_HOST=your_host.reg.ru
DB_PORT=3306
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
DATABASE_URL=mysql+aiomysql://user:password@host:3306/dbname
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

### Шаг 2: Создание директории для логов

```bash
mkdir -p /opt/bot_moderator/logs
chmod 755 /opt/bot_moderator/logs
```

### Шаг 3: Проверка структуры

```bash
ls -la /opt/bot_moderator
# Должны быть: bot/, docker-compose.yml, Dockerfile, .env, requirements.txt
```

---

## 🐳 Запуск через Docker Compose

### Шаг 1: Сборка образа

```bash
cd /opt/bot_moderator
docker-compose build
```

### Шаг 2: Запуск в фоновом режиме

```bash
docker-compose up -d
```

### Шаг 3: Проверка работы

```bash
# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f moderator-bot

# Остановка (если нужно)
docker-compose down
```

---

## 🔄 Настройка автозапуска (systemd)

### Создание systemd сервиса

```bash
sudo nano /etc/systemd/system/bot-moderator.service
```

Вставьте:
```ini
[Unit]
Description=Telegram Bot Moderator
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/bot_moderator
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

### Активация автозапуска

```bash
# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable bot-moderator.service

# Запуск сервиса
sudo systemctl start bot-moderator.service

# Проверка статуса
sudo systemctl status bot-moderator.service
```

---

## 🔧 Альтернатива: Docker Compose с restart policy

Уже настроено в `docker-compose.yml`:
```yaml
restart: unless-stopped
```

Это означает, что контейнер будет автоматически перезапускаться при перезагрузке сервера.

---

## 📊 Мониторинг и управление

### Просмотр логов

```bash
# Все логи
docker-compose logs moderator-bot

# Последние 50 строк
docker-compose logs --tail=50 moderator-bot

# Логи в реальном времени
docker-compose logs -f moderator-bot

# Логи за последний час
docker-compose logs --since 1h moderator-bot
```

### Перезапуск бота

```bash
# Перезапуск контейнера
docker-compose restart moderator-bot

# Пересборка и перезапуск (после изменений кода)
docker-compose up -d --build
```

### Остановка/Запуск

```bash
# Остановка
docker-compose down

# Запуск
docker-compose up -d
```

### Проверка использования ресурсов

```bash
# Использование ресурсов контейнером
docker stats telegram-moderator-bot

# Общая информация о контейнерах
docker ps -a
```

---

## 🔒 Безопасность

### 1. Настройка файрвола

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 22/tcp  # SSH
sudo ufw enable

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

### 2. Защита .env файла

```bash
chmod 600 /opt/bot_moderator/.env
```

### 3. Регулярные обновления

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Обновление Docker образов
docker-compose pull
```

---

## 🛠️ Устранение проблем

### Бот не запускается

```bash
# Проверка логов
docker-compose logs moderator-bot

# Проверка статуса
docker-compose ps

# Проверка .env файла
cat /opt/bot_moderator/.env
```

### Ошибки подключения к БД

1. Проверьте параметры в `.env`
2. Убедитесь, что БД доступна извне (firewall на reg.ru)
3. Проверьте логи: `docker-compose logs moderator-bot`

### Контейнер постоянно перезапускается

```bash
# Просмотр логов ошибок
docker-compose logs moderator-bot | grep -i error

# Проверка ресурсов
docker stats telegram-moderator-bot
```

### Обновление кода

```bash
cd /opt/bot_moderator

# Если используете Git
git pull

# Пересборка и перезапуск
docker-compose up -d --build
```

---

## 📝 Чеклист деплоя

- [ ] VPS настроен и обновлен
- [ ] Docker установлен
- [ ] Проект загружен на VPS
- [ ] Файл .env создан и заполнен
- [ ] Директория logs создана
- [ ] Образ собран: `docker-compose build`
- [ ] Бот запущен: `docker-compose up -d`
- [ ] Бот работает: проверены логи
- [ ] Автозапуск настроен (systemd или restart policy)
- [ ] Файрвол настроен
- [ ] Тестирование в Telegram группе

---

## 🎯 Быстрый старт (краткая версия)

```bash
# 1. Подключение к VPS
ssh root@your_vps_ip

# 2. Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh

# 3. Создание директории
mkdir -p /opt/bot_moderator && cd /opt/bot_moderator

# 4. Загрузка проекта (выберите способ)
# Git, SCP или архив

# 5. Создание .env
nano .env  # Заполните данные

# 6. Запуск
docker-compose up -d --build

# 7. Проверка
docker-compose logs -f moderator-bot
```

---

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose logs moderator-bot`
2. Проверьте статус: `docker-compose ps`
3. Проверьте .env файл
4. Убедитесь, что БД доступна

---

**Готово! Бот теперь работает 24/7 на вашем VPS!** 🎉

