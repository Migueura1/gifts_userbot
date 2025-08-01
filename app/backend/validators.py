from aiogram.types import Message


async def _get_int_from_message(message: Message) -> int | None:
    try:
        integer = int(message.text)

        return integer
    except Exception:
        return None


async def _is_positive(num: int) -> bool:
    return num >= 0


async def validate_supply(message: Message):
    supply = await _get_int_from_message(message)

    if supply == None or not await _is_positive(supply) or supply > 500000:
        return None
    
    return supply
    

async def validate_price_from(message: Message):
    price_from = await _get_int_from_message(message)

    if price_from == None or not await _is_positive(price_from) or price_from > 100000:
        return None
    
    return price_from



async def validate_price_to(message: Message):
    price_to = await _get_int_from_message(message)

    if price_to == None or not await _is_positive(price_to) or price_to > 100000:
        return None
    
    return price_to


async def validate_channel_id(message: Message) -> int | None:
    try:
        id = int(message.text)

        if id >= 0:
            raise Exception
        
        if not str(id).startswith('-100'):
            raise Exception
        
        return id

    except Exception as e:
        return None
    

async def validate_amount(message: Message):
    try:
        amount = int(message.text)

        if amount < 1 or amount > 50000:
            return None
        
        return amount
    except Exception:
        return None