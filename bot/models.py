"""
МОДУЛЬ: Модели данных
Определяет структуры данных для действий бота.
Независимый модуль - используется другими модулями.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BotAction:
    """Модель действия бота-модератора."""
    
    action_type: str  # message_deleted, user_banned, user_warned и т.д.
    user_id: int
    chat_id: int
    username: Optional[str] = None
    message_text: Optional[str] = None
    reason: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Преобразует модель в словарь для сохранения в БД."""
        return {
            "action_type": self.action_type,
            "user_id": self.user_id,
            "username": self.username,
            "chat_id": self.chat_id,
            "message_text": self.message_text,
            "reason": self.reason,
        }


class ActionType:
    """Типы действий бота."""
    
    MESSAGE_DELETED = "message_deleted"
    USER_BANNED = "user_banned"
    USER_UNBANNED = "user_unbanned"
    USER_WARNED = "user_warned"
    USER_MUTED = "user_muted"
    USER_UNMUTED = "user_unmuted"

