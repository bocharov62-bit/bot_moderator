"""
МОДУЛЬ: Конфигурация проекта
Отвечает за загрузку и валидацию переменных окружения.
Независимый модуль - может использоваться отдельно.
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Класс для хранения конфигурации бота."""
    
    def __init__(self):
        """Загружает переменные окружения из .env файла."""
        load_dotenv()
        
        # Telegram Bot
        self.BOT_TOKEN: str = self._get_env("BOT_TOKEN", required=True)
        
        # Database (MySQL)
        self.DB_HOST: str = self._get_env("DB_HOST", required=True)
        self.DB_PORT: int = int(self._get_env("DB_PORT", default="3306"))
        self.DB_USER: str = self._get_env("DB_USER", required=True)
        self.DB_PASSWORD: str = self._get_env("DB_PASSWORD", required=True)
        self.DB_NAME: str = self._get_env("DB_NAME", required=True)
        
        # Database URL (опционально, может быть сформирован автоматически)
        self.DATABASE_URL: Optional[str] = self._get_env("DATABASE_URL", required=False)
        
        # Logging
        self.LOG_LEVEL: str = self._get_env("LOG_LEVEL", default="INFO")
        self.LOG_FILE: str = self._get_env("LOG_FILE", default="logs/bot.log")
        
        # Формируем DATABASE_URL если не указан
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
    
    def _get_env(self, key: str, default: Optional[str] = None, required: bool = False) -> str:
        """
        Получает переменную окружения.
        
        Args:
            key: Имя переменной
            default: Значение по умолчанию
            required: Обязательна ли переменная
            
        Returns:
            Значение переменной
            
        Raises:
            ValueError: Если переменная обязательна, но не найдена
        """
        value = os.getenv(key, default)
        
        if required and not value:
            raise ValueError(
                f"Переменная окружения {key} обязательна, но не установлена. "
                f"Проверьте файл .env"
            )
        
        return value
    
    def get_db_config(self) -> dict:
        """
        Возвращает конфигурацию для подключения к БД.
        
        Returns:
            Словарь с параметрами подключения
        """
        return {
            "host": self.DB_HOST,
            "port": self.DB_PORT,
            "user": self.DB_USER,
            "password": self.DB_PASSWORD,
            "db": self.DB_NAME,
        }


# Глобальный экземпляр конфигурации
config = Config()

