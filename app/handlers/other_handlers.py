from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from lexicon import other_start

router = Router()


@router.message(CommandStart())
async def start_other(message: Message):
    await message.answer(
        text=await other_start()
    )