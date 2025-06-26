print(f"▶️ handle_age_confirmation вызван с: chat_id={chat_id}, text={text}")
from handlers.buttons import get_age_confirmation_buttons, get_main_menu

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
            "reply_markup": get_main_menu()
        }
    else:
        return {
            "text": "🚫 Доступ запрещён. Повторите /start, если вам уже исполнилось 18."
        }

def request_age_confirmation():
    return {
        "text": "Подтвердите, пожалуйста, что вам есть 18 лет:",
        "reply_markup": get_age_confirmation_buttons()
    }
