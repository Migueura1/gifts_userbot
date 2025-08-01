from aiogram import F, Router, Bot
from aiogram.filters import CommandStart, Command, StateFilter, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, FSInputFile
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from pyrogram import Client

from typing import Dict, Any

from fsm import UserStates
from loguru import logger

from config import NOT_SET, MAX_CHANNELS_COUNT, default_logs_path

import os
import lexicon
from keyboards import create_inline_kb, create_channels_kb
from backend import validate_supply, validate_price_from, validate_price_to, validate_channel_id, validate_amount
from db import requests
from filters import AllowUserFilter

from backend.autobuy import autobuy_test, get_gifts_by_command


router = Router()
router.message.filter(AllowUserFilter())
router.callback_query.filter(AllowUserFilter())


start_kb = create_inline_kb(2,'test_autobuy', 'price_from', 'price_to', 'supply', 'link_channels')

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        text=await lexicon.start_page(),
        reply_markup=start_kb
    )


############################################################################
# ⚙️ ИЗМЕНЕНИЕ ПАРАМЕТРОВ САППЛАЯ И ЦЕНЫ
############################################################################
@router.callback_query(F.data == 'supply')
async def change_supply(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=await lexicon.supply_page(),
        reply_markup=create_inline_kb(1, 'cancel', 'clear_supply')
    )

    await state.set_state(UserStates.fill_supply)


@router.callback_query(F.data == 'clear_supply')
async def clear_supply(callback: CallbackQuery, state: FSMContext):
    requests.update_supply_limit(NOT_SET)

    await callback.message.edit_text(
        text=await lexicon.start_page(),
        reply_markup=start_kb
    )

    await state.clear()


@router.message(StateFilter(UserStates.fill_supply))
async def fill_supply(message: Message, state: FSMContext):
    supply = await validate_supply(message)

    if not supply:
        await message.answer(
            text='❌ Неверное значение, пробуйте еще раз..',
            reply_markup=create_inline_kb(1, 'cancel')
        )
        return
    
    requests.update_supply_limit(supply)

    await message.answer(
            text=f'✅ Сапплай обновлен: <code>{supply} шт.</code>',
            reply_markup=create_inline_kb(1, 'ok')
        )
    
    await state.clear()


###############################################################
@router.callback_query(F.data == 'price_from')
async def change_price_from(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=await lexicon.price_from_page(),
        reply_markup=create_inline_kb(1, 'cancel', 'clear_price_from')
    )

    await state.set_state(UserStates.fill_price_from)


@router.callback_query(F.data == 'clear_price_from')
async def clear_price_from(callback: CallbackQuery, state: FSMContext):
    requests.update_price_from(NOT_SET)

    await callback.message.edit_text(
        text=await lexicon.start_page(),
        reply_markup=start_kb
    )

    await state.clear()


@router.message(StateFilter(UserStates.fill_price_from))
async def fill_price_from(message: Message, state: FSMContext):
    price_from = await validate_price_from(message)

    if not price_from:
        await message.answer(
            text='❌ Неверное значение, пробуйте еще раз..',
            reply_markup=create_inline_kb(1, 'cancel')
        )
        return
    
    requests.update_price_from(price_from)

    await message.answer(
            text=f'✅ Цена ОТ обновлена: <code>{price_from} ⭐️</code>',
            reply_markup=create_inline_kb(1, 'ok')
        )
    
    await state.clear()


###############################################################
@router.callback_query(F.data == 'price_to')
async def change_price_to(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=await lexicon.price_to_page(),
        reply_markup=create_inline_kb(1, 'cancel', 'clear_price_to')
    )

    await state.set_state(UserStates.fill_price_to)


@router.callback_query(F.data == 'clear_price_to')
async def clear_price_to(callback: CallbackQuery, state: FSMContext):
    requests.update_price_to(NOT_SET)

    await callback.message.edit_text(
        text=await lexicon.start_page(),
        reply_markup=start_kb
    )

    await state.clear()


@router.message(StateFilter(UserStates.fill_price_to))
async def fill_price_to(message: Message, state: FSMContext):
    price_to = await validate_price_to(message)

    if not price_to:
        await message.answer(
            text='❌ Неверное значение, пробуйте еще раз..',
            reply_markup=create_inline_kb(1, 'cancel')
        )
        return
    
    requests.update_price_to(price_to)

    await message.answer(
            text=f'✅ Цена ДО обновлена: <code>{price_to} ⭐️</code>',
            reply_markup=create_inline_kb(1, 'ok')
        )
    
    await state.clear()



############################################################################
# 🔗 ПРИВЯЗКА КАНАЛОВ
############################################################################
@router.callback_query(F.data == 'link_channels')
async def link_channels(callback: CallbackQuery):
    config = requests.load_config()

    await callback.message.edit_text(
        text=await lexicon.channels(config['linked_channels']),
        reply_markup=create_channels_kb(config['linked_channels'])
    )


@router.callback_query(F.data.startswith('channel_'))
async def channel_(callback: CallbackQuery):
    id = callback.data.split('_')[-1]
    
    await callback.message.edit_text(
        text=await lexicon.channel_(id),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f'Отвязать', callback_data=f'unlink_{id}')],
            [InlineKeyboardButton(text=f'🏘 На главную', callback_data=f'cancel')],
        ])
    )


@router.callback_query(F.data.startswith('unlink_'))
async def channel_(callback: CallbackQuery):
    id = callback.data.split('_')[-1]

    requests.remove_channel(id)

    await link_channels(callback)


@router.callback_query(F.data == 'add_channel')
async def add_channel(callback: CallbackQuery, state: FSMContext):
    config = requests.load_config()
    if len(config['linked_channels']) >= MAX_CHANNELS_COUNT:
        await callback.answer(
            text=f'Достигнуто максимальное кол-во каналов: {MAX_CHANNELS_COUNT}',
            show_alert=True
        )
        return
    
    await callback.message.edit_text(
        text=await lexicon.add_channel(),
        reply_markup=create_inline_kb(1, 'cancel')
    )

    await state.set_state(UserStates.fill_channel)


@router.message(StateFilter(UserStates.fill_channel))
async def fill_channel(message: Message, bot: Bot, state: FSMContext):
    channel_id = await validate_channel_id(message)

    if not channel_id:
        await message.answer(
            text="Неверный формат ID, попробуйте еще раз.",
            reply_markup=create_inline_kb(1, 'cancel')
        )
        return

    else:
        # проверка на то, правильно ли добавлен канал
        try:
            linked_group = await bot.get_chat(chat_id=channel_id)
            
            if linked_group.type != 'channel':
                await message.answer(
                    text="Это не канал.",
                    reply_markup=create_inline_kb(1, 'cancel')
                )
                return
        except Exception as e:
            await message.answer(
                text='Не получилось подключиться к каналу',
                reply_markup=create_inline_kb(1, 'cancel')
            )
            return
        
        config = requests.load_config()
        if channel_id in config["linked_channels"]:
            await message.answer(
                text="Этот канал уже привязан.",
                reply_markup=create_inline_kb(1, 'cancel')
            )
            return 

        channel_name = linked_group.title
        requests.add_channel(channel_id, channel_name)

        await message.answer(
            text=f'✅ Канал привязан: <code>{channel_name}[{channel_id}]</code>',
            reply_markup=create_inline_kb(1, 'ok')
        )

        await state.clear()    


############################################################################
# ⭐️ РЕФАНД
############################################################################
@router.message(Command("refund"))
async def cmd_refund(
    message: Message,
    bot: Bot,
    command: CommandObject,
):
    transaction_id = command.args
    if transaction_id is None:
        await message.answer(
            text='Не предоставили Id транзы',
            reply_markup=create_inline_kb(1, 'ok')
        )
        return
    try:
        await bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=transaction_id
        )
        await message.answer(
            text='refunded',
            reply_markup=create_inline_kb(1, 'ok')
        )

        logger.info("Выполнен возврат.")
    except TelegramBadRequest as error:
        if "CHARGE_NOT_FOUND" in error.message:
            text = 'refund-code-not-found'
        elif "CHARGE_ALREADY_REFUNDED" in error.message:
            text = "refund-already-refunded"
        else:
            # При всех остальных ошибках – такой же текст,
            # как и в первом случае
            text = "refund-code-not-found"
        await message.answer(text, reply_markup=create_inline_kb(1, 'ok'))
        return
    
############################################################################
# /gifts
############################################################################
@router.message(Command('gifts'))
async def get_gifts(message: Message, **data: Dict[str, Any]):
    await message.answer(
        text='<b>Получаю доступные подарки</b>'
    )

    client: Client = data["client"]

    gifts = await get_gifts_by_command(client)

    text = "Доступные подарки:\n\n"

    for g in gifts:
        text += f"{g.sticker.emoji} | {g.id} | {g.price}\n"
    
    await message.answer(
        text=text
    )


############################################################################
# 📥 ВЫГРУЗКА ЛОГОВ
############################################################################
@router.message(Command('logs'))
async def logs_dump(message: Message):
    log_dir = default_logs_path
    files = ["info.log", "errors.log"]

    for filename in files:
        path = os.path.join(log_dir, filename)
        if os.path.exists(path):
            await message.answer_document(document=FSInputFile(path))
        else:
            await message.answer(f"Файл <code>{filename}</code> не найден.")

############################################################################
# 🎁 ТЕСТ СНАЙПЕРА
############################################################################
@router.callback_query(F.data == 'test_autobuy')
async def test_autobuy(callback: CallbackQuery):
    await callback.message.answer(
        text='<b>Вы уверены, что хотите провести тестирование снайпера?</b>\n\n<blockquote>Бот купит 3 🧸 по 15 ⭐️ с вашего баланса</blockquote>',
        reply_markup=create_inline_kb(2, 'start_test', 'cancel')
    )


@router.callback_query(F.data == 'start_test')
async def start_test(callback: CallbackQuery, **data: Dict[str, Any]):
    await callback.message.edit_text(
        text='<b>Начинаю тестирование..</b>'
    )

    client: Client = data["client"]

    await autobuy_test(client)

    await callback.message.edit_text(
        text='<b>Тестирование завершено, смотрите логи и каналы/профиль.</b>'
    )

############################################################################
# ❌ ОТМЕНА и ОКЕЙ
############################################################################
@router.callback_query(F.data == 'cancel')
@router.callback_query(F.data == 'ok')
async def process_profile_back(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=await lexicon.start_page(),
        reply_markup=start_kb
    )

    await state.clear()



    

