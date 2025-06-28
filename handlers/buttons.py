from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from urllib.parse import quote

def get_main_menu():
    keyboard = [[KeyboardButton("🛍 Каталог")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True).to_dict()

def get_category_buttons():
    categories = [
        "Виски", "Коньяк и Арманьяк", "Кальвадос",
        "Водка", "Джин", "Шампанское и игристое",
        "Вино", "Крепкое вино", "Другие"
    ]
    keyboard = [
        [InlineKeyboardButton(cat, callback_data=f"category|{quote(cat)}|1")]
        for cat in categories
    ]
    return InlineKeyboardMarkup(keyboard).to_dict()
