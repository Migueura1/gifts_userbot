from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from pyrogram import Client
from pyrogram import enums
from pyrogram.enums import ParseMode

from loguru import logger

import json
import asyncio

from pathlib import Path

from config import load_config, default_json_path, NOT_SET, status
from logger import init_logger
from keyboards import set_main_menu
from backend.autobuy import autobuy_worker
from handlers import get_routers


async def main():
    # загрузка конфига
    config = load_config()

    # инициализация хранилища с настройками снайпа если оно не создано
    SNIPE_CONFIG_PATH = Path(default_json_path)

    if not SNIPE_CONFIG_PATH.exists():
        data = {
            "supply_limit": NOT_SET,
            "price_from": NOT_SET,
            "price_to": NOT_SET,
            "linked_channels": {}
        }
        with open(SNIPE_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)


    # инициализация юзербота
    app = Client(
        "my_acc", config.client.api_id, config.client.api_hash,
        device_model="iPhone 16 Pro",
        system_version="IOS 18.5",
        app_version="11.14 (31192)",
        lang_pack="ios",
        lang_code="ru",
        client_platform=enums.ClientPlatform.IOS,
        parse_mode=ParseMode.HTML
    )

    # инициализация бота и диспетчера
    bot = Bot(config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # настройка главного меню
    await set_main_menu(bot)

    # настройка логгера
    init_logger(bot, config.logs.id)

    # запуск механизма снайпинга
    await app.start()
    asyncio.create_task(autobuy_worker(app))

    # подключение роутеров
    dp.include_routers(*get_routers())

    # проверка лицензии
    if status == -2:
        logger.error("Лицензия не найдена!")
        return

    # запуск бота
    await bot.delete_webhook(drop_pending_updates=True)  
    logger.info(f"Бот запущен..")  
    await dp.start_polling(bot, client=app)
    await app.stop()
    

if __name__ == "__main__":
    asyncio.run(main())