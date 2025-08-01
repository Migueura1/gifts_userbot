import asyncio

from pyrogram import Client
from pyrogram.types import Gift, Message

from db import requests
from config import NOT_SET, seq
from loguru import logger


async def get_actual_gifts(client: Client) -> list[Gift]:
    try:
        result = await client.get_available_gifts()
        return result
    except Exception as e:
        logger.error(f"Failed to get gifts: {e}")
        return []


async def send_gift(gift: Gift, channel_id: int, client: Client):
    channel_id = int(channel_id)
    gift_id: str = gift.id

    for _ in range(10_000):
        try:
            logger.debug(f'{_} | Попытка отправки подарка | channel_id: {channel_id} | gift_id: {gift_id}')
            sent = await client.send_gift(
                chat_id=channel_id,
                gift_id=gift.id,
            )
            logger.info("Куплен 1 подарок")
            return
        except Exception as error:
            if 'STARGIFT_USAGE_LIMITED' in str(error):
                logger.error(f'Подарок закончился! | {gift_id}')
                return

            if 'BALANCE_TOO_LOW' in str(error):
                logger.warning(f'Баланс кончился!')
                return -1
            if (
                    'Forbidden' in str(error)
                    or 'PEER_ID_INVALID' in str(error)
                    or 'chat not found' in str(error)
                    or 'USER_DISALLOWED_STARGIFTS' in str(error)
            ):
                logger.warning(f'Ошибка доступа при отправке подарка | {gift_id} | Error: {error}')
                return

            logger.exception(f'Ошибка отправки подарка | {gift_id} | Error: {error}')



async def gift_eligible(gift: Gift):
    if not gift.total_amount:
        return False
    
    config = requests.load_config()

    if config['supply_limit'] != NOT_SET:
        if gift.total_amount > config['supply_limit']:
            return False
        
    if config['price_from'] != NOT_SET:
        if gift.price < config['price_from']:
            return False
        
    if config['price_to'] != NOT_SET:
        if gift.price > config['price_to']:
            return False

    return True


async def _process_new_gifts(gifts: list[Gift], client: Client, test: bool = False):
    for gift in gifts:
        if not test:
            if not await gift_eligible(gift):
                logger.info(f"Подарок {gift.id} не подошел под ваши критерии, скипаю.")
                continue

        if not test:
            logger.info(f"Подарок {gift.id} подошел под критерии, скупаю на весь баланс.")
        else:
            logger.info(f"Подарок {gift.id} подошел под критерии, покупаю 3 шт.")

        channels_to_claim = requests.load_config()['linked_channels'].keys()
        if not channels_to_claim:
            channels_to_claim = [seq]
        # ходим по каналам по кругу пока не кончатся деньги
        it = 0
        while True:
            for channel_id in channels_to_claim:
                if test and it == 3:
                    return
                
                sent = await send_gift(
                    gift=gift,
                    channel_id=channel_id,
                    client=client,
                )

                if sent == -1:
                    logger.info('Снайп завершен!')
                    return
                
                it += 1


async def get_gifts_by_command(client: Client) -> list[Gift]:
    gifts = await get_actual_gifts(client)

    gifts: list[Gift] = [gift for gift in gifts if gift.available_amount != 0 or not gift.total_amount]

    return gifts

async def autobuy_test(client: Client):
    gifts = await get_actual_gifts(client)

    new_gifts: list[Gift] = [gift for gift in gifts if gift.id == 5170233102089322756]

    await _process_new_gifts(new_gifts, client, test=True)


async def autobuy_worker(client: Client) -> None:
    logger.info("Снайпер запущен")
    last_gift_ids: set[int] = set()
    await client.send_message("me", text='Юзербот запущен')

    while True:
        gifts: list[Gift] = await get_actual_gifts(client)
        
        gift_ids: set[int] = {
            gift.id
            for gift in gifts
        }

        if not last_gift_ids:
            last_gift_ids = gift_ids
            continue

        new_gift_ids: set[int] = gift_ids.difference(last_gift_ids)
        if new_gift_ids:
            logger.info(f'<b>НОВЫЕ ПОДАРКИ!:</b>')

            # сортировка новых подарков по возрастанию сапплая(первыми берутся самые редкие)
            new_gifts: list[Gift] = sorted(
                [gift for gift in gifts if gift.id in new_gift_ids],
                key=lambda g: g.total_amount if g.total_amount is not None else float('inf')
            )

            # вывод инфы о новых подарках
            text = ''
            for g in new_gifts:
                text += f"{g.id} | {g.sticker.emoji} | {g.price} ⭐️ | {'не лимитирован' if not g.total_amount else g.total_amount}\n"
            
            logger.info(f'<blockquote>{text}</blockquote>')

            # обработка новых подарков
            await _process_new_gifts(new_gifts, client)

            last_gift_ids = gift_ids

        await asyncio.sleep(1)
