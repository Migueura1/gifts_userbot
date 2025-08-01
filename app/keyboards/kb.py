from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder


from lexicon import BUTTONS as LEXICON


def create_inline_kb(
    width: int,
    first_btn: str,
    *args: str,
    **kwargs: str,
) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    
    if first_btn:
        last = InlineKeyboardButton(text=LEXICON[first_btn] if first_btn in LEXICON else first_btn, callback_data=first_btn)
        kb_builder.row(last, width=1)

    buttons: list[InlineKeyboardButton] = []

    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=LEXICON[button] if button in LEXICON else button,
                callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))

    kb_builder.row(*buttons, width=width)

    return kb_builder.as_markup()


def create_channels_kb(channels: dict) -> InlineKeyboardMarkup:
    inline_kb = []
    if channels:
        for id, name in channels.items():
            inline_kb.append([InlineKeyboardButton(text=f'{name}', callback_data=f'channel_{id}')])

    inline_kb.append(
        [InlineKeyboardButton(text='➕ Добавить канал', callback_data='add_channel')],
    )

    inline_kb.append(
        [InlineKeyboardButton(text='🏘 На главную', callback_data='cancel')],
    )

    return InlineKeyboardMarkup(inline_keyboard=inline_kb)

