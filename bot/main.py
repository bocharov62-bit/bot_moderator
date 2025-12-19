"""
МОДУЛЬ: Точка входа бота
Инициализирует и запускает Telegram-бота.
Координирует работу всех модулей.
"""

import asyncio
import signal
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import config
from bot.database import db
from bot.handlers import router
from bot.logger import logger


# Глобальные переменные для graceful shutdown
bot: Bot = None
dp: Dispatcher = None


async def on_startup():
    """Выполняется при запуске бота."""
    logger.info("=" * 50)
    logger.info("Запуск Telegram-бота модератора")
    logger.info("=" * 50)
    
    # Подключаемся к базе данных
    try:
        await db.connect()
        logger.info("Подключение к БД успешно установлено")
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {e}")
        logger.error("Бот будет работать без сохранения в БД")
    
    logger.info("Бот успешно запущен и готов к работе")


async def on_shutdown():
    """Выполняется при остановке бота."""
    logger.info("Остановка бота...")
    
    # Закрываем подключение к БД
    try:
        await db.disconnect()
        logger.info("Подключение к БД закрыто")
    except Exception as e:
        logger.error(f"Ошибка при закрытии подключения к БД: {e}")
    
    logger.info("Бот остановлен")


def signal_handler(sig, frame):
    """Обработчик сигналов для graceful shutdown."""
    logger.info("Получен сигнал остановки, завершаем работу...")
    if dp:
        asyncio.create_task(dp.stop_polling())
    sys.exit(0)


async def main():
    """Главная функция запуска бота."""
    global bot, dp
    
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Инициализируем бота
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Инициализируем диспетчер
    dp = Dispatcher()
    
    # Регистрируем роутер с обработчиками
    dp.include_router(router)
    
    # Регистрируем функции startup и shutdown
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    try:
        # Запускаем polling
        logger.info("Начинаем polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Критическая ошибка при работе бота: {e}")
        raise
    finally:
        await on_shutdown()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получено прерывание от пользователя")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)

