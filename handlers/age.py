from handlers.buttons import get_age_confirmation_buttons, get_main_menu
from handlers.language import get_translated_text

# Хранилище подтверждённых пользователей
confirmed_users = set()

def is_confirmed(chat_id: int) -> bool:
    return chat_id in confirmed_users

def confirm_user(chat_id: int):
    print(f"✅ Пользователь {chat_id} подтвердил возраст")
    confirmed_users.add(chat_id)

def handle_age_confirmation(chat_id: int, text: str):
    cleaned = text.strip().lower()
    print(f"📩 Обработка подтверждения возраста: chat_id={chat_id}, text='{text}'")
    
    if cleaned == "age:yes":
        confirm_user(chat_id)
        return {
            "text": "✅ Спасибо! Меню доступно:",
            "reply_markup": get_main_menu(chat_id)
        }
    else:
        return {
            "text": "🚫 Доступ запрещён. Повторите /start, если вам уже исполнилось 18."
        }

def request_age_confirmation(chat_id: int):
    return {
        "text": get_translated_text(chat_id, "age_confirm"),
        "reply_markup": get_age_confirmation_buttons(chat_id)
    }
