from telegram import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu():
    keyboard = [
        [KeyboardButton("🛍 Каталог")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True).to_dict()
