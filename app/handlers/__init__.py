from aiogram import Router
from . import user_handlers, other_handlers 


def get_routers() -> list[Router]:
    return [
        user_handlers.router,
        other_handlers.router
    ]