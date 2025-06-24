from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_reply_markup():
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

# ✅ Кнопки подтверждения возраста
def get_age_confirmation_buttons():
    keyboard = [
        [
            InlineKeyboardButton("Да, мне есть 18", callback_data="age:yes"),
            InlineKeyboardButton("Нет", callback_data="age:no")
        ]
    ]
    return InlineKeyboardMarkup(keyboard).to_dict()
