from loguru import logger
import asyncio
from config import default_logs_path
import os

class TelegramLogHandler:
    def __init__(self, bot, info_channel):
        self.bot = bot
        self.info_channel = info_channel

    async def send_log(self, message: str):
        try:
            await self.bot.send_message(chat_id=self.info_channel, text=message)
        except Exception as e:
            logger.debug(f"Не удалось отправить лог в Telegram: {e}")

    def __call__(self, message):
        record = message.record
        level = record["level"].name
        time_str = record["time"].strftime("%d.%m.%Y %H:%M:%S")
        log_text = f"[{time_str}] <b>{level}</b> | {record['message']}"
        asyncio.create_task(self.send_log(log_text))


def init_logger(bot, logs_channel_id):
    logger.add(
        os.path.join(default_logs_path, 'info.log'),
        format="<green>{time:DD.MM.YYYY HH:mm:ss}</green> | <level>{level}</level> | {message}",
        level="INFO",
        rotation="1000 KB",
        compression="zip"
    )

    logger.add(
        os.path.join(default_logs_path, 'errors.log'),
        format="<green>{time:DD.MM.YYYY HH:mm:ss}</green> | <level>{level}</level> | {message}",
        level="ERROR",
        rotation="1000 KB",
        compression="zip"
    )

    logger.add(
        TelegramLogHandler(
            bot,
            logs_channel_id,
        ),
        level="INFO",
    )
