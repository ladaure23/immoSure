import logging
from telegram import Bot
from telegram.error import TelegramError
from app.config import settings

logger = logging.getLogger(__name__)

_bot: Bot | None = None


def get_bot() -> Bot | None:
    global _bot
    if _bot is None and settings.telegram_bot_token:
        _bot = Bot(token=settings.telegram_bot_token)
    return _bot


async def send_notification(chat_id: str | None, message: str) -> None:
    if not chat_id:
        return
    bot = get_bot()
    if not bot:
        return
    try:
        await bot.send_message(chat_id=int(chat_id), text=message)
    except TelegramError as e:
        logger.warning("Telegram notification échouée (chat_id=%s): %s", chat_id, e)
