# handlers/language.py

from handlers.buttons import get_main_menu

# Временное хранилище языков пользователей
user_languages: dict[int, str] = {}

def set_user_language(chat_id: int, lang: str):
    user_languages[chat_id] = lang

def get_user_language(chat_id: int) -> str:
    return user_languages.get(chat_id, "ru")

async def handle_language_selection(chat_id: int, send_message):
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🇷🇺 Русский", "callback_data": "lang:ru"},
                {"text": "🇬🇧 English", "callback_data": "lang:en"},
                {"text": "🇪🇸 Español", "callback_data": "lang:es"},
            ]
        ]
    }
    return await send_message(chat_id, "🌐 Выберите язык / Choose a language:", reply_markup=keyboard)

def get_translated_text(text_id: str, lang: str) -> str:
    translations = {
        "menu_prompt": {
            "ru": "Нажмите 🛍 Каталог",
            "en": "Press 🛍 Catalog",
            "es": "Presione 🛍 Catálogo",
        },
        "age_confirm": {
            "ru": "Подтвердите, пожалуйста, что вам есть 18 лет:",
            "en": "Please confirm that you are over 18:",
            "es": "Por favor confirme que tiene más de 18 años:",
        },
    }
    return translations.get(text_id, {}).get(lang, text_id)
