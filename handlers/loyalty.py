import requests
from config import SUPABASE_URL, SUPABASE_KEY
from datetime import datetime

def register_loyalty_card(chat_id: int) -> bool:
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    # Проверка существования записи
    check_url = f"{SUPABASE_URL}/rest/v1/loyalty_cards?select=id&Chat_ID=eq.{chat_id}"
    try:
        check_resp = requests.get(check_url, headers=headers)
        if check_resp.status_code == 200 and check_resp.json():
            return False  # Уже есть карта
    except Exception as e:
        print("❌ Ошибка при проверке карты:", e)
        return False

    # Создание новой записи
    insert_url = f"{SUPABASE_URL}/rest/v1/loyalty_cards"
    payload = [{
        "Chat_ID": str(chat_id),
        "tier": "bronze",
        "total_orders": 0,
        "birthday": None,
        "created_at": datetime.utcnow().isoformat()
    }]

    try:
        insert_resp = requests.post(insert_url, headers=headers, json=payload)
        insert_resp.raise_for_status()
        return True
    except Exception as e:
        print("❌ Ошибка регистрации карты:", e)
        return False
