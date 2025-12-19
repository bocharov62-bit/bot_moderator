"""
МОДУЛЬ: Работа с базой данных
Обеспечивает подключение к MySQL и операции с БД.
Использует bot/config.py для получения параметров подключения.
"""

import aiomysql
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from bot.config import config
from bot.models import BotAction
from bot.logger import logger


class Database:
    """Класс для работы с базой данных MySQL."""
    
    def __init__(self):
        """Инициализация подключения к БД."""
        self.pool: Optional[aiomysql.Pool] = None
    
    async def connect(self):
        """Создаёт пул соединений с базой данных."""
        try:
            db_config = config.get_db_config()
            self.pool = await aiomysql.create_pool(
                host=db_config["host"],
                port=db_config["port"],
                user=db_config["user"],
                password=db_config["password"],
                db=db_config["db"],
                minsize=1,
                maxsize=10,
                autocommit=True,
                charset="utf8mb4",
                use_unicode=True,
            )
            logger.info(f"Подключение к БД установлено: {db_config['host']}:{db_config['port']}/{db_config['db']}")
        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            raise
    
    async def disconnect(self):
        """Закрывает пул соединений."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            logger.info("Подключение к БД закрыто")
    
    @asynccontextmanager
    async def get_connection(self):
        """Контекстный менеджер для получения соединения из пула."""
        if not self.pool:
            raise RuntimeError("Пул соединений не инициализирован. Вызовите connect() сначала.")
        
        async with self.pool.acquire() as conn:
            yield conn
    
    async def save_action(self, action: BotAction) -> bool:
        """
        Сохраняет действие бота в базу данных.
        
        Args:
            action: Объект BotAction для сохранения
            
        Returns:
            True если успешно, False в случае ошибки
        """
        try:
            async with self.get_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO bot_actions 
                        (action_type, user_id, username, chat_id, message_text, reason)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (
                            action.action_type,
                            action.user_id,
                            action.username,
                            action.chat_id,
                            action.message_text,
                            action.reason,
                        )
                    )
                    logger.debug(f"Действие сохранено в БД: {action.action_type} для user_id={action.user_id}")
                    return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении действия в БД: {e}")
            return False
    
    async def get_stats(self, chat_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Получает статистику действий.
        
        Args:
            chat_id: ID чата (если None, возвращает для всех чатов)
            limit: Максимальное количество записей
            
        Returns:
            Список словарей с данными действий
        """
        try:
            async with self.get_connection() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    if chat_id:
                        await cur.execute(
                            """
                            SELECT * FROM bot_actions 
                            WHERE chat_id = %s 
                            ORDER BY created_at DESC 
                            LIMIT %s
                            """,
                            (chat_id, limit)
                        )
                    else:
                        await cur.execute(
                            """
                            SELECT * FROM bot_actions 
                            ORDER BY created_at DESC 
                            LIMIT %s
                            """,
                            (limit,)
                        )
                    return await cur.fetchall()
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            return []
    
    async def get_action_count(self, action_type: str, chat_id: Optional[int] = None) -> int:
        """
        Получает количество действий определённого типа.
        
        Args:
            action_type: Тип действия
            chat_id: ID чата (если None, считает для всех чатов)
            
        Returns:
            Количество действий
        """
        try:
            async with self.get_connection() as conn:
                async with conn.cursor() as cur:
                    if chat_id:
                        await cur.execute(
                            "SELECT COUNT(*) FROM bot_actions WHERE action_type = %s AND chat_id = %s",
                            (action_type, chat_id)
                        )
                    else:
                        await cur.execute(
                            "SELECT COUNT(*) FROM bot_actions WHERE action_type = %s",
                            (action_type,)
                        )
                    result = await cur.fetchone()
                    return result[0] if result else 0
        except Exception as e:
            logger.error(f"Ошибка при подсчёте действий: {e}")
            return 0


# Глобальный экземпляр базы данных
db = Database()

