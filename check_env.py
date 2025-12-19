#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Скрипт для проверки файла .env"""

import os
import sys
from dotenv import load_dotenv

# Настройка кодировки для Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Загружаем .env
load_dotenv()

print("=" * 60)
print("ПРОВЕРКА ФАЙЛА .env")
print("=" * 60)
print()

# Обязательные переменные
required_vars = {
    "BOT_TOKEN": "Токен Telegram-бота (получить у @BotFather)",
    "DB_HOST": "Хост MySQL базы данных",
    "DB_PORT": "Порт MySQL (обычно 3306)",
    "DB_USER": "Имя пользователя БД",
    "DB_PASSWORD": "Пароль БД",
    "DB_NAME": "Имя базы данных",
}

# Опциональные переменные
optional_vars = {
    "DATABASE_URL": "URL подключения (формируется автоматически, если не указан)",
    "LOG_LEVEL": "Уровень логирования (по умолчанию: INFO)",
    "LOG_FILE": "Путь к файлу логов (по умолчанию: logs/bot.log)",
}

print("ОБЯЗАТЕЛЬНЫЕ ПЕРЕМЕННЫЕ:")
print("-" * 60)
missing = []
for var, description in required_vars.items():
    value = os.getenv(var)
    if not value or value.startswith("your_") or value == "":
        status = "[X] НЕ ЗАПОЛНЕНО"
        missing.append(var)
    else:
        # Скрываем чувствительные данные
        if var in ["BOT_TOKEN", "DB_PASSWORD"]:
            display_value = value[:10] + "..." if len(value) > 10 else "***"
        else:
            display_value = value
        status = f"[OK] Заполнено: {display_value}"
    
    print(f"{var:20} | {status}")
    print(f"{'':20}   {description}")
    print()

print("ОПЦИОНАЛЬНЫЕ ПЕРЕМЕННЫЕ:")
print("-" * 60)
for var, description in optional_vars.items():
    value = os.getenv(var)
    if value:
        if var == "DATABASE_URL" and ("user:password" in value or "your_" in value):
            status = "[!] Шаблонное значение (будет сформировано автоматически)"
        else:
            status = f"[OK] Установлено: {value}"
    else:
        status = "[ ] Не установлено (используется значение по умолчанию)"
    
    print(f"{var:20} | {status}")
    print(f"{'':20}   {description}")
    print()

print("=" * 60)
if missing:
    print(f"[X] ОШИБКА: Не заполнены обязательные переменные: {', '.join(missing)}")
    print()
    print("Заполните эти переменные в файле .env перед запуском бота!")
    exit(1)
else:
    print("[OK] ВСЕ ОБЯЗАТЕЛЬНЫЕ ПЕРЕМЕННЫЕ ЗАПОЛНЕНЫ")
    print()
    
    # Проверка формата BOT_TOKEN
    bot_token = os.getenv("BOT_TOKEN", "")
    if bot_token and ":" in bot_token:
        print("[OK] Формат BOT_TOKEN корректен (содержит ':')")
    elif bot_token:
        print("[!] BOT_TOKEN может быть некорректным (должен содержать ':')")
    
    # Проверка DATABASE_URL
    db_url = os.getenv("DATABASE_URL", "")
    if db_url and ("user:password" in db_url or "your_" in db_url):
        print("[!] DATABASE_URL содержит шаблонные значения, будет сформирован автоматически")
    elif db_url:
        print("[OK] DATABASE_URL заполнен")
    
    print()
    print("[OK] Файл .env готов к использованию!")

print("=" * 60)

