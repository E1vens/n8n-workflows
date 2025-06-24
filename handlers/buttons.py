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

