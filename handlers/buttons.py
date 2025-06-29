from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from urllib.parse import quote
from handlers.language import get_translated_text

# ✅ Кнопки подтверждения возраста (мультиязычные)
def get_age_confirmation_buttons(chat_id: int):
    yes_text = get_translated_text(chat_id, "btn_age_yes") or "Да, мне есть 18"
    no_text = get_translated_text(chat_id, "btn_age_no") or "Нет"
    keyboard = [
        [
            InlineKeyboardButton(yes_text, callback_data="age:yes"),
            InlineKeyboardButton(no_text, callback_data="age:no")
        ]
    ]
    return InlineKeyboardMarkup(keyboard).to_dict()

# ✅ Главное меню с мультиязычными кнопками
def get_main_menu(chat_id: int):
    keyboard = [
        [
            KeyboardButton(f"🛍 {get_translated_text(chat_id, 'btn_catalog')}"),
            KeyboardButton(f"👑 {get_translated_text(chat_id, 'btn_elite')}")
        ],
        [
            KeyboardButton(f"🤖 {get_translated_text(chat_id, 'btn_ai')}"),
            KeyboardButton(f"ℹ️ {get_translated_text(chat_id, 'btn_info')}")
        ],
        [
            KeyboardButton(f"🌐 {get_translated_text(chat_id, 'btn_language')}"),
            KeyboardButton(f"🎁 {get_translated_text(chat_id, 'btn_loyalty')}")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True).to_dict()

# ✅ Кнопки выбора категории (пока статично — можно адаптировать позже)
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

# ✅ Кнопки выбора языка
def get_language_buttons():
    keyboard = [
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang:ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang:en"),
            InlineKeyboardButton("🇪🇸 Español", callback_data="lang:es")
        ]
    ]
    return InlineKeyboardMarkup(keyboard).to_dict()
