from handlers.language import get_translated_text, get_user_language
from handlers.buttons import get_age_confirmation_buttons, get_main_menu

# Хранилище подтверждённых пользователей
confirmed_users = set()

def is_confirmed(chat_id: int) -> bool:
    return chat_id in confirmed_users

def confirm_user(chat_id: int):
    print(f"✅ Пользователь {chat_id} подтвердил возраст")
    confirmed_users.add(chat_id)

def request_age_confirmation(chat_id: int) -> dict:
    return {
        "text": (
            "🔞 *Возрастное ограничение!*\n\n"
            "Этот бот содержит информацию, предназначенную только для совершеннолетних.\n\n"
            "Пожалуйста, подтвердите, что вам уже исполнилось 18 лет:"
        ),
        "reply_markup": get_age_confirmation_buttons(chat_id)
    }

def handle_age_confirmation(chat_id: int, text: str) -> dict:
    cleaned = text.strip().lower()
    print(f"📩 Обработка подтверждения возраста: chat_id={chat_id}, text='{text}'")

    if cleaned == "age:yes":
        confirm_user(chat_id)
        return {
            "text": (
                "✅ *Возраст подтверждён!*\n\n"
                "Теперь вы можете просматривать каталог и использовать все функции бота. 🍷"
            ),
            "reply_markup": get_main_menu(chat_id),
            "confirmed": True
        }
    else:
        return {
            "text": "🚫 Доступ запрещён. Повторите /start, если вам уже исполнилось 18.",
            "confirmed": False
        }
