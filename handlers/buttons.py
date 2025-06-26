from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

# ✅ Кнопки подтверждения возраста (разделены по строкам)
def get_age_confirmation_buttons():
    return {
        "inline_keyboard": [
            [
                {"text": "Да, мне есть 18", "callback_data": "age:yes"},
                {"text": "Нет", "callback_data": "age:no"}
            ]
        ]
    }


# ✅ Категории товаров (inline-кнопки)
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
        [InlineKeyboardButton(text=title, callback_data=f"category:{title}")]
        for title in categories
    ]
    return InlineKeyboardMarkup(keyboard).to_dict()

# ✅ Главное меню (reply-кнопки)
def get_main_menu():
    keyboard = [
        [KeyboardButton("🛍 Каталог"), KeyboardButton("🤖 ИИ консультант")],
        [KeyboardButton("ℹ️ Информация о товаре"), KeyboardButton("🌐 Выбрать язык")],
        [KeyboardButton("🎁 Карта лояльности")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True).to_dict()

# ✅ Кнопка выхода из ИИ-консультанта (reply-кнопка)
def get_ai_exit_button():
    keyboard = [
        [KeyboardButton("🔙 Выйти из ИИ")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True).to_dict()
