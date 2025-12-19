-- SQL-скрипт для создания таблиц в MySQL
-- Выполнить через dbhub или phpMyAdmin на reg.ru

CREATE TABLE IF NOT EXISTS bot_actions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action_type VARCHAR(50) NOT NULL COMMENT 'Тип действия: message_deleted, user_banned, user_warned и т.д.',
    user_id BIGINT NOT NULL COMMENT 'ID пользователя Telegram',
    username VARCHAR(255) COMMENT 'Имя пользователя Telegram',
    chat_id BIGINT NOT NULL COMMENT 'ID чата',
    message_text TEXT COMMENT 'Текст сообщения (если применимо)',
    reason TEXT COMMENT 'Причина действия',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Время создания записи',
    INDEX idx_user_id (user_id),
    INDEX idx_chat_id (chat_id),
    INDEX idx_created_at (created_at),
    INDEX idx_action_type (action_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Таблица для хранения действий бота-модератора';

