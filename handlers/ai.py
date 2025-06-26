# handlers/ai.py

active_ai_users = set()

def is_ai_active(chat_id: int) -> bool:
    return chat_id in active_ai_users

def activate_ai(chat_id: int):
    active_ai_users.add(chat_id)

def deactivate_ai(chat_id: int):
    active_ai_users.discard(chat_id)
