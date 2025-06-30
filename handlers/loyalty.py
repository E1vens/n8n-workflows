import requests
from config import SUPABASE_URL, SUPABASE_KEY
from datetime import datetime

def register_loyalty_card(chat_id: int) -> str:
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    check_url = f"{SUPABASE_URL}/rest/v1/loyalty_cards?select=id&Chat_ID=eq.{chat_id}"

    try:
        resp = requests.get(check_url, headers=headers)
        if resp.status_code == 200:
            if resp.json():
                return "exists"
        else:
            print("❌ Проверка карты: ошибка", resp.status_code, resp.text)
            return "error"
    except Exception as e:
        print("❌ Ошибка при проверке карты:", e)
        return "error"

    # Если не существует — создаём
    insert_url = f"{SUPABASE_URL}/rest/v1/loyalty_cards"
    payload = [{
        "Chat_ID": str(chat_id),
        "tier": "bronze",
        "total_orders": 0,
        "birthday": None,
        "created_at": datetime.utcnow().isoformat()
    }]

    try:
        resp = requests.post(insert_url, headers=headers, json=payload)
        resp.raise_for_status()
        return "created"
    except Exception as e:
        print("❌ Ошибка регистрации карты:", e)
        return "error"
