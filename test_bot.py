#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестирования Telegram-бота модератора
"""

import asyncio
import sys
from dotenv import load_dotenv
import os

# Настройка кодировки для Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()

async def test_database():
    """Тест подключения к базе данных"""
    print("=" * 60)
    print("ТЕСТ 1: Подключение к базе данных")
    print("=" * 60)
    
    try:
        from bot.database import db
        await db.connect()
        print("[OK] Подключение к БД успешно")
        
        # Проверка структуры таблицы
        async with db.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("DESCRIBE bot_actions")
                columns = await cur.fetchall()
                print(f"[OK] Таблица bot_actions существует ({len(columns)} колонок)")
        
        await db.disconnect()
        return True
    except Exception as e:
        print(f"[ERROR] Ошибка подключения к БД: {e}")
        return False

async def test_filters():
    """Тест фильтров нецензурных слов"""
    print("\n" + "=" * 60)
    print("ТЕСТ 2: Фильтры нецензурных слов")
    print("=" * 60)
    
    try:
        from bot.filters import message_filter
        
        # Тестовые сообщения
        test_messages = [
            ("Привет, как дела?", False, "Обычное сообщение"),
            ("Ты дурак!", True, "Оскорбление"),
            ("Идиот какой-то", True, "Оскорбление"),
            ("Хорошая погода сегодня", False, "Обычное сообщение"),
            ("Это сволочь", True, "Оскорбление"),
        ]
        
        passed = 0
        failed = 0
        
        for message, should_detect, description in test_messages:
            result = message_filter.contains_bad_words(message)
            if result == should_detect:
                print(f"[OK] '{message[:30]}...' - {description}")
                passed += 1
            else:
                print(f"[FAIL] '{message[:30]}...' - {description} (ожидалось: {should_detect}, получено: {result})")
                failed += 1
        
        print(f"\nРезультат: {passed} прошло, {failed} провалено")
        return failed == 0
    except Exception as e:
        print(f"[ERROR] Ошибка тестирования фильтров: {e}")
        return False

async def test_config():
    """Тест конфигурации"""
    print("\n" + "=" * 60)
    print("ТЕСТ 3: Конфигурация")
    print("=" * 60)
    
    try:
        from bot.config import config
        
        checks = [
            ("BOT_TOKEN", config.BOT_TOKEN, lambda x: x and ":" in x and not x.startswith("your_")),
            ("DB_HOST", config.DB_HOST, lambda x: x and not x.startswith("your_")),
            ("DB_PORT", config.DB_PORT, lambda x: isinstance(x, int) and x > 0),
            ("DB_USER", config.DB_USER, lambda x: x and not x.startswith("your_")),
            ("DB_PASSWORD", config.DB_PASSWORD, lambda x: x and not x.startswith("your_")),
            ("DB_NAME", config.DB_NAME, lambda x: x and not x.startswith("your_")),
            ("LOG_LEVEL", config.LOG_LEVEL, lambda x: x in ["DEBUG", "INFO", "WARNING", "ERROR"]),
        ]
        
        passed = 0
        failed = 0
        
        for name, value, check in checks:
            try:
                if check(value):
                    # Скрываем чувствительные данные
                    display_value = str(value)[:20] + "..." if len(str(value)) > 20 else str(value)
                    if name in ["BOT_TOKEN", "DB_PASSWORD"]:
                        display_value = "***скрыто***"
                    print(f"[OK] {name}: {display_value}")
                    passed += 1
                else:
                    print(f"[FAIL] {name}: некорректное значение")
                    failed += 1
            except Exception as e:
                print(f"[ERROR] {name}: ошибка проверки - {e}")
                failed += 1
        
        print(f"\nРезультат: {passed} прошло, {failed} провалено")
        return failed == 0
    except Exception as e:
        print(f"[ERROR] Ошибка тестирования конфигурации: {e}")
        return False

async def test_database_operations():
    """Тест операций с базой данных"""
    print("\n" + "=" * 60)
    print("ТЕСТ 4: Операции с базой данных")
    print("=" * 60)
    
    try:
        from bot.database import db
        from bot.models import BotAction, ActionType
        
        await db.connect()
        
        # Тест сохранения действия
        test_action = BotAction(
            action_type=ActionType.MESSAGE_DELETED,
            user_id=123456789,
            chat_id=-1001234567890,
            username="test_user",
            message_text="Тестовое сообщение",
            reason="Тест сохранения"
        )
        
        result = await db.save_action(test_action)
        if result:
            print("[OK] Сохранение действия в БД успешно")
        else:
            print("[FAIL] Не удалось сохранить действие в БД")
            await db.disconnect()
            return False
        
        # Тест получения статистики
        stats = await db.get_stats(limit=5)
        if isinstance(stats, list):
            print(f"[OK] Получение статистики успешно ({len(stats)} записей)")
        else:
            print("[FAIL] Ошибка получения статистики")
            await db.disconnect()
            return False
        
        # Тест подсчёта действий
        count = await db.get_action_count(ActionType.MESSAGE_DELETED)
        if isinstance(count, int):
            print(f"[OK] Подсчёт действий успешен (всего: {count})")
        else:
            print("[FAIL] Ошибка подсчёта действий")
            await db.disconnect()
            return False
        
        await db.disconnect()
        return True
    except Exception as e:
        print(f"[ERROR] Ошибка тестирования операций с БД: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_logger():
    """Тест логирования"""
    print("\n" + "=" * 60)
    print("ТЕСТ 5: Логирование")
    print("=" * 60)
    
    try:
        from bot.logger import logger
        
        logger.debug("Тестовое сообщение DEBUG")
        logger.info("Тестовое сообщение INFO")
        logger.warning("Тестовое сообщение WARNING")
        logger.error("Тестовое сообщение ERROR")
        
        print("[OK] Логирование работает (проверьте файл logs/bot.log)")
        return True
    except Exception as e:
        print(f"[ERROR] Ошибка тестирования логирования: {e}")
        return False

async def main():
    """Главная функция тестирования"""
    print("\n" + "=" * 60)
    print("НАЧАЛО ТЕСТИРОВАНИЯ TELEGRAM-БОТА МОДЕРАТОРА")
    print("=" * 60)
    print()
    
    tests = [
        ("Конфигурация", test_config),
        ("Фильтры", test_filters),
        ("Подключение к БД", test_database),
        ("Операции с БД", test_database_operations),
        ("Логирование", test_logger),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] Критическая ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))
    
    # Итоговый отчёт
    print("\n" + "=" * 60)
    print("ИТОГОВЫЙ ОТЧЁТ")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print("\n" + "-" * 60)
    print(f"Всего тестов: {total}")
    print(f"Успешно: {passed}")
    print(f"Провалено: {total - passed}")
    print("=" * 60)
    
    if passed == total:
        print("\n[SUCCESS] Все тесты пройдены успешно!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} тест(ов) провалено")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

