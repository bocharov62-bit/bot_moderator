"""
МОДУЛЬ: Обработчики команд и сообщений
Обрабатывает команды и сообщения от пользователей.
Использует другие модули: filters, database, logger, models.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

from bot.filters import message_filter
from bot.database import db
from bot.models import BotAction, ActionType
from bot.logger import logger


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start."""
    welcome_text = (
        "👋 Привет! Я бот-модератор.\n\n"
        "Я помогаю поддерживать порядок в чате:\n"
        "• Удаляю сообщения с нецензурными выражениями\n"
        "• Блокирую нарушителей\n"
        "• Веду статистику модерации\n\n"
        "Используйте /help для списка команд."
    )
    await message.answer(welcome_text)
    logger.info(f"Команда /start от пользователя {message.from_user.id}")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help."""
    help_text = (
        "📋 Доступные команды:\n\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n"
        "/stats - Показать статистику модерации\n\n"
        "Бот автоматически удаляет сообщения с нецензурными выражениями."
    )
    await message.answer(help_text)
    logger.info(f"Команда /help от пользователя {message.from_user.id}")


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Обработчик команды /stats - показывает статистику модерации."""
    try:
        chat_id = message.chat.id
        
        # Получаем статистику
        deleted_count = await db.get_action_count(ActionType.MESSAGE_DELETED, chat_id)
        banned_count = await db.get_action_count(ActionType.USER_BANNED, chat_id)
        warned_count = await db.get_action_count(ActionType.USER_WARNED, chat_id)
        
        stats_text = (
            f"📊 Статистика модерации для этого чата:\n\n"
            f"🗑️ Удалено сообщений: {deleted_count}\n"
            f"🚫 Заблокировано пользователей: {banned_count}\n"
            f"⚠️ Выдано предупреждений: {warned_count}"
        )
        
        await message.answer(stats_text)
        logger.info(f"Команда /stats от пользователя {message.from_user.id} в чате {chat_id}")
        
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        await message.answer("❌ Ошибка при получении статистики.")


@router.message(F.text)
async def handle_message(message: Message):
    """
    Обработчик всех текстовых сообщений.
    Проверяет сообщения на наличие запрещённых слов.
    """
    # Пропускаем команды
    if message.text and message.text.startswith("/"):
        return
    
    # Проверяем сообщение на запрещённые слова
    if message.text and message_filter.contains_bad_words(message.text):
        try:
            # Удаляем сообщение
            await message.delete()
            
            # Сохраняем действие в БД
            action = BotAction(
                action_type=ActionType.MESSAGE_DELETED,
                user_id=message.from_user.id,
                chat_id=message.chat.id,
                username=message.from_user.username,
                message_text=message.text[:500],  # Ограничиваем длину
                reason="Содержит нецензурные выражения"
            )
            await db.save_action(action)
            
            # Логируем
            logger.warning(
                f"Удалено сообщение от пользователя {message.from_user.id} "
                f"(@{message.from_user.username}) в чате {message.chat.id}"
            )
            
            # Опционально: отправляем предупреждение пользователю
            try:
                warning_text = (
                    f"⚠️ {message.from_user.first_name}, ваше сообщение было удалено "
                    f"за нарушение правил чата."
                )
                await message.answer(warning_text)
            except Exception as e:
                logger.debug(f"Не удалось отправить предупреждение: {e}")
                
        except TelegramBadRequest as e:
            # Бот не может удалить сообщение (нет прав или сообщение уже удалено)
            logger.warning(f"Не удалось удалить сообщение: {e}")
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")


@router.message(Command("ban"))
async def cmd_ban(message: Message):
    """
    Обработчик команды /ban - бан пользователя.
    Требует прав администратора.
    """
    # Проверяем, что команда вызвана в группе/супергруппе
    if message.chat.type not in ["group", "supergroup"]:
        await message.answer("❌ Эта команда работает только в группах.")
        return
    
    # Проверяем, что пользователь - администратор
    if not message.from_user:
        return
    
    try:
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ["administrator", "creator"]:
            await message.answer("❌ Только администраторы могут использовать эту команду.")
            return
    except Exception as e:
        logger.error(f"Ошибка при проверке прав администратора: {e}")
        return
    
    # Получаем ID пользователя для бана (из ответа на сообщение или из аргумента)
    if message.reply_to_message:
        user_to_ban = message.reply_to_message.from_user
    else:
        # Парсим аргумент команды
        args = message.text.split()[1:] if message.text else []
        if not args:
            await message.answer("❌ Использование: /ban [user_id] или ответьте на сообщение пользователя.")
            return
        try:
            user_id = int(args[0])
            user_to_ban = await message.bot.get_chat_member(message.chat.id, user_id)
            user_to_ban = user_to_ban.user
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
            return
    
    try:
        # Баним пользователя
        await message.bot.ban_chat_member(message.chat.id, user_to_ban.id)
        
        # Сохраняем действие в БД
        action = BotAction(
            action_type=ActionType.USER_BANNED,
            user_id=user_to_ban.id,
            chat_id=message.chat.id,
            username=user_to_ban.username,
            reason=f"Забанен администратором {message.from_user.id}"
        )
        await db.save_action(action)
        
        await message.answer(f"🚫 Пользователь {user_to_ban.first_name} (@{user_to_ban.username}) забанен.")
        logger.info(f"Пользователь {user_to_ban.id} забанен в чате {message.chat.id}")
        
    except Exception as e:
        logger.error(f"Ошибка при бане пользователя: {e}")
        await message.answer(f"❌ Ошибка при бане пользователя: {e}")


@router.message(Command("unban"))
async def cmd_unban(message: Message):
    """
    Обработчик команды /unban - разбан пользователя.
    Требует прав администратора.
    """
    # Аналогично команде /ban
    if message.chat.type not in ["group", "supergroup"]:
        await message.answer("❌ Эта команда работает только в группах.")
        return
    
    try:
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ["administrator", "creator"]:
            await message.answer("❌ Только администраторы могут использовать эту команду.")
            return
    except Exception as e:
        logger.error(f"Ошибка при проверке прав администратора: {e}")
        return
    
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer("❌ Использование: /unban [user_id]")
        return
    
    try:
        user_id = int(args[0])
        await message.bot.unban_chat_member(message.chat.id, user_id)
        
        # Сохраняем действие в БД
        action = BotAction(
            action_type=ActionType.USER_UNBANNED,
            user_id=user_id,
            chat_id=message.chat.id,
            reason=f"Разбанен администратором {message.from_user.id}"
        )
        await db.save_action(action)
        
        await message.answer(f"✅ Пользователь {user_id} разбанен.")
        logger.info(f"Пользователь {user_id} разбанен в чате {message.chat.id}")
        
    except Exception as e:
        logger.error(f"Ошибка при разбане пользователя: {e}")
        await message.answer(f"❌ Ошибка при разбане пользователя: {e}")

