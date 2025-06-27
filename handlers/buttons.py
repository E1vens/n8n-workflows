from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

# ✅ Кнопки подтверждения возраста (разделены по строкам)
def get_age_confirmation_buttons():
    keyboard = [
        [
            InlineKeyboardButton("Да, мне есть 18", callback_data="age:yes"),
            InlineKeyboardButton("Нет", callback_data="age:no")
        ]
    ]
    return InlineKeyboardMarkup(keyboard).to_dict()  # ← ЭТО важно!

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
    return InlineKeyboardMarkup(keyboard).to_dict()  # ← ТОЖЕ .to_dict()

# ✅ Главное меню (reply-кнопки)
def get_main_menu():
    keyboard = [
        [KeyboardButton("🛍 Каталог"), KeyboardButton("👑 Элитный алкоголь")],
        [KeyboardButton("🤖 ИИ консультант"), KeyboardButton("ℹ️ Информация о компании и партнёрах")],
        [KeyboardButton("🌐 Выбрать язык"), KeyboardButton("🎁 Карта лояльности")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True).to_dict()

# ✅ Кнопка выхода из ИИ-консультанта (reply-кнопка)
def get_ai_exit_button():
    keyboard = [
        [KeyboardButton("🔙 Выйти из ИИ")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True).to_dict()
