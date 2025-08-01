from aiogram.filters import BaseFilter
from aiogram.types import Message
from config import seq


class AllowUserFilter(BaseFilter):
    async def __call__(self, message: Message):
        return str(message.from_user.id) == str(seq)