"""
МОДУЛЬ: Логирование
Настройка системы логирования для бота.
Независимый модуль - может использоваться в любом месте проекта.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from bot.config import config


def setup_logger(name: str = "bot", log_file: Optional[str] = None) -> logging.Logger:
    """
    Настраивает и возвращает логгер.
    
    Args:
        name: Имя логгера
        log_file: Путь к файлу логов (если None, используется из config)
        
    Returns:
        Настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
    
    # Очищаем существующие обработчики
    logger.handlers.clear()
    
    # Формат логов
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Обработчик для файла
    log_file_path = log_file or config.LOG_FILE
    
    # Создаём директорию для логов если её нет
    log_path = Path(log_file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# Глобальный логгер
logger = setup_logger()

