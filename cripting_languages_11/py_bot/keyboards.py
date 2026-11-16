from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton # класс для тг-ботов. клавиатура и кнопка

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆 Топ игроков", callback_data="top")], # при нажатии на кнопку, бот получит "топ"
        [InlineKeyboardButton(text="📊 Моя статистика", callback_data="stats")],
        [InlineKeyboardButton(text="🎖 Достижения", callback_data="achievements")],
        [InlineKeyboardButton(text="🗺 Инфо о карте", callback_data="map_info")],
        [InlineKeyboardButton(text="📤 Загрузить CSV", callback_data="upload")],
        [InlineKeyboardButton(text="🔔 Уведомления", callback_data="watch_toggle")]
    ])

def back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="menu")]
    ])