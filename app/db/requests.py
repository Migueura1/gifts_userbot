import json
from pathlib import Path
from config import default_json_path, NOT_SET
from loguru import logger

CONFIG_PATH = Path(default_json_path)


# чтение конфига
def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# запись конфига
def save_config(data: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# 🔧 Обновление supply_limit
def update_supply_limit(new_limit: int):
    config = load_config()
    config["supply_limit"] = new_limit
    save_config(config)

    logger.info(f"supply_limit обновлен: {new_limit if new_limit != NOT_SET else 'не установлено'}")


# 🔧 Обновление price_from
def update_price_from(price: float):
    config = load_config()
    config["price_from"] = price
    save_config(config)

    logger.info(f"price_from обновлен: {price if price != NOT_SET else 'не установлено'}")


# 🔧 Обновление price_to
def update_price_to(price: float):
    config = load_config()
    config["price_to"] = price
    save_config(config)

    logger.info(f"price_to обновлен: {price if price != NOT_SET else 'не установлено'}")


# ➕ Добавить канал
def add_channel(channel_id: int, channel_name: str):
    config = load_config()
    str_id = str(channel_id)
    if str_id not in config["linked_channels"]:
        config["linked_channels"][str_id] = channel_name
        save_config(config)

        logger.info(f"Канал привязан: {channel_name}[<code>{channel_id}</code>]")
        
    logger.info(f"Канал уже привязан: {channel_name}[<code>{channel_id}</code>]")



# ➖ Удалить канал
def remove_channel(channel_id: str):
    config = load_config()
    
    del config['linked_channels'][channel_id]

    save_config(config)

    logger.info(f"Канал отвязан: {channel_id}")