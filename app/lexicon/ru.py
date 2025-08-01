import db.requests as req
from config import NOT_SET


BUTTONS = {
    'supply': "Supply",
    'price_from': "Цена ОТ",
    'price_to': "Цена ДО",
    'link_channels': "🔗 Привязка каналов",
    'test_autobuy': "🎁 Тест снайпера",
    'cancel': '❌ Отмена',
    'ok': 'Окей',
    'clear_supply': "Сбросить",
    'clear_price_from': "Сбросить",
    'clear_price_to': "Сбросить",
    'unlink': "Отвязать",
    'enter_stars': "⭐️ Пополнить баланс",
    'start_test': '🎁 Начать',
}

LEXICON_COMMANDS_RU = {
    'start': 'Перезапуск бота'
}


async def start_page() -> str:
    config = req.load_config()
    text = f"<b>⚙️ Ваша конфигурация:</b>\n\n"
    text += f"Supply: <code>до {str(config['supply_limit']) + ' шт.' if config['supply_limit'] != NOT_SET else 'не установлено'}</code>\n"
    text += f"Цена от: <code>{str(config['price_from']) + ' ⭐️' if config['price_from'] != NOT_SET else 'не установлено'}</code>\n"
    text += f"Цена до: <code>{str(config['price_to']) + ' ⭐️' if config['price_to'] != NOT_SET else 'не установлено'}</code>\n\n"

    if config['linked_channels']:
        linked_channels = config['linked_channels']
        text += '<b>🔗 Привязанные каналы:</b>\n'

        text += '<blockquote>'
        for id, name in linked_channels.items():
            text += f'• {name}[<code>{id}</code>]\n'
        text += '</blockquote>'
    else:
        text += '<blockquote>⚠️ Привязанных каналов нет, подарки будут отправлены на ваш профиль.</blockquote>'

    text += '\n\n<b>Подсказка:</b> Чтобы ловить самые редкие подарки - не трогайте параметры <code>Цена ОТ</code> и <code>Цена ДО</code>, просто выставите минимальный supply; если не выставлять никакие из настроек - бот возьмет самый редкий вышедший подарок. '

    text += '\n\n<b>Подсказка 2:</b> Вы можете протестировать работоспособность бота, перейдя в раздел 🎁<code>Тест Снайпера</code>'

    text += '\n\n <b>Подсказка 3: </b>Используйте команду /logs для выгрузки логов с бота и /refund [id транзакции] для возврата звезд.'

    return text


async def supply_page() -> str:
    config = req.load_config()

    text = "<b>⚙️ Меню настройки сапплая:</b>\n\n"
    text += f"Сапплай до: <code>{str(config['supply_limit']) + ' шт.' if config['supply_limit'] != NOT_SET else 'не установлено'}</code>\n\n"
    text += f'<blockquote>Введите новое значение:</blockquote>'

    return text


async def price_from_page() -> str:
    config = req.load_config()

    text = "<b>⚙️ Меню настройки Цены ОТ:</b>\n\n"
    text += f"Цена ОТ: <code>{str(config['price_from']) + ' ⭐️' if config['price_from'] != NOT_SET else 'не установлено'}</code>\n\n"
    text += f'<blockquote>Введите новое значение:</blockquote>'

    return text


async def price_to_page() -> str:
    config = req.load_config()

    text = "<b>⚙️ Меню настройки Цены ДО:</b>\n\n"
    text += f"Цена ДО: <code>{str(config['price_to']) + ' ⭐️' if config['price_to'] != NOT_SET else 'не установлено'}</code>\n\n"
    text += f'<blockquote>Введите новое значение:</blockquote>'

    return text


async def channels(channels: dict) -> str:
    text = '<b>🔗 Меню привязки каналов:</b>\n\n'

    if not channels:
        text += '<blockquote>⚠️ У вас нет ни одного привязанного канала, подарки будут отправлены на ваш профиль.</blockquote>'
    
    return text
    

async def channel_(id: str) -> str:
    config = req.load_config()
    channel_name = config['linked_channels'][id]
    channel_id = id

    text = '<b>Управление каналом:</b>\n\n'

    text += '<blockquote>'
    text += f'<b>ID:</b> <code>{channel_id}</code>\n'
    text += f'<b>Название:</b> <code>{channel_name}</code>\n'
    text += '</blockquote>'

    return text


async def add_channel() -> str:
    text = (
        '<b>🔗 Привязка нового канала</b>\n\n'
        '<blockquote>1) Создайте канал(не группу), лучше частный\n'
        '2) Добавьте этого бота в канал\n'
        '3) Пришлите сюда ID канала(можно получить, переслав любое сообщение в @getmyid_bot)\n\n'
        '<b>Бот сам проверит правильность выполненных действий и подвяжет канал.</b></blockquote>'
    )

    return text

async def other_start() -> str:
    text = (
        "<b>Проверка не пройдена!</b>\n\n"
        "Возможно вы не оплатили лицензию бота, за покупкой обратитесь к <b>@white_fIow.</b>"
    )

    return text