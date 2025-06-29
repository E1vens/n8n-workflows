from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from urllib.parse import quote

# ✅ Кнопки подтверждения возраста
def get_age_confirmation_buttons():
    keyboard = [
        [
            InlineKeyboardButton("Да, мне есть 18", callback_data="age:yes"),
            InlineKeyboardButton("Нет", callback_data="age:no")
        ]
    ]
    return InlineKeyboardMarkup(keyboard).to_dict()

# ✅ Главное меню
def get_main_menu():
    keyboard = [
        [KeyboardButton("🛍 Каталог"), KeyboardButton("👑 Элитный алкоголь")],
        [KeyboardButton("🤖 ИИ консультант"), KeyboardButton("ℹ️ Информация о компании и партнёрах")],
        [KeyboardButton("🌐 Выбрать язык"), KeyboardButton("🎁 Карта лояльности")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True).to_dict()

# ✅ Кнопки выбора категории (inline)
def get_category_buttons():
    categories = [
        "Виски",
        "Коньяк и Арманьяк",
        "Кальвадос",
        "Водка",
        "Джин",
        "Шампанское и игристое",
        "Вино",
        "Крепкое вино",
        "Другие"
    ]
    keyboard = [
        [InlineKeyboardButton(text=title, callback_data=f"category|{quote(title)}|1")]
        for title in categories
    ]
    return InlineKeyboardMarkup(keyboard).to_dict()

# ✅ Кнопки выбора языка (inline)
def get_language_buttons():
    keyboard = [
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang:ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang:en"),
            InlineKeyboardButton("🇪🇸 Español", callback_data="lang:es")
        ]
    ]
    return InlineKeyboardMarkup(keyboard).to_dict()
