#from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY
from datetime import datetime

#supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Регистрируем пользователя в loyalty_cards (если нет)
async def register_loyalty_card(chat_id: int):
    # Проверка: есть ли уже карта
    existing = supabase.table("loyalty_cards").select("id").eq("Chat_ID", str(chat_id)).execute()
    if existing.data:
        return False  # Уже есть

    # Создание новой записи
    supabase.table("loyalty_cards").insert({
        "Chat_ID": str(chat_id),
        "tier": "bronze",
        "total_orders": 0,
        "birthday": None,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    return True
