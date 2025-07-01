import requests
from typing import Optional, List
from datetime import datetime
from config import SUPABASE_URL, SUPABASE_KEY

# 📦 Получение уникальных категорий
def get_distinct_categories():
    url = f"{SUPABASE_URL}/rest/v1/documents?select=metadata"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        raw_categories = [item["metadata"]["category"] for item in response.json()
                          if "metadata" in item and item["metadata"].get("category")]
        categories = sorted(set(filter(None, raw_categories)))
        return categories
    except Exception as e:
        print("❌ Ошибка получения категорий:", e)
        return []

# 📦 Товары по категории
def get_top_products_by_category(category: str, limit: int = 5):
    url = f"{SUPABASE_URL}/rest/v1/documents"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Range": f"0-{limit - 1}",
        "Range-Unit": "items"
    }

    params = {
        "select": "*",
        "metadata->>category": f"eq.{category}",
        "order": "price.asc"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Ошибка получения товаров по категории '{category}':", e)
        return []

# 📦 Товары по категории (с пагинацией)
def match_documents_by_category(category: str, sort: str = "asc", page: int = 1, per_page: int = 10) -> list:
    url = f"{SUPABASE_URL}/rest/v1/documents"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Range-Unit": "items",
        "Range": f"{(page - 1) * per_page}-{(page * per_page - 1)}"
    }

    params = {
        "select": "*",
        "metadata->>category": f"eq.{category}",
        "order": f"price.{sort}"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("❌ Supabase category error:", str(e))
        print("📦 Ответ Supabase:", response.text)
        return []

# 🔍 Векторный поиск товаров через RPC
def call_match_documents(
    embedding: list[float],
    top_k: int = 5,
    max_price: float | None = None,
    min_strength: float | None = None,
    max_strength: float | None = None
) -> list[dict]:
    url = f"{SUPABASE_URL}/rest/v1/rpc/match_documents"
    payload = {
        "query_embedding": embedding,
        "match_count": top_k
    }

    if max_price is not None:
        payload["max_price"] = max_price
    if min_strength is not None:
        payload["min_strength"] = min_strength
    if max_strength is not None:
        payload["max_strength"] = max_strength

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        print("📥 Ответ от Supabase:", data)  # 👈 вот это нужно вставить
        return data
    except Exception as e:
        print("❌ Ошибка Supabase match_documents:", e)
        print("📦 Ответ:", response.text)
        return []


# 🧾 Проверка и регистрация карты лояльности
def register_loyalty_card(chat_id: int) -> bool:
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    check_url = f"{SUPABASE_URL}/rest/v1/loyalty_cards?select=id&Chat_ID=eq.{chat_id}"
    try:
        check_resp = requests.get(check_url, headers=headers)
        if check_resp.status_code == 200 and check_resp.json():
            return False  # Уже существует
    except Exception as e:
        print("❌ Ошибка при проверке карты:", e)
        return False

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

# 📤 Получение информации о карте лояльности
def get_loyalty_card(chat_id: int) -> Optional[dict]:
    url = f"{SUPABASE_URL}/rest/v1/loyalty_cards?Chat_ID=eq.{chat_id}&select=*"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data[0] if data else None
    except Exception as e:
        print("❌ Ошибка получения карты:", e)
        return None

# 🧠 Получить активный режим ИИ
def get_ai_mode(chat_id: int) -> Optional[str]:
    url = f"{SUPABASE_URL}/rest/v1/user_settings?chat_id=eq.{chat_id}&select=ai_mode"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data[0]["ai_mode"] if data else None
    except Exception as e:
        print("❌ Ошибка получения режима ИИ:", e)
        return None

# 🧠 Установить/обновить режим ИИ
def set_ai_mode(chat_id: int, mode: str):
    url = f"{SUPABASE_URL}/rest/v1/user_settings"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    payload = [{"chat_id": chat_id, "ai_mode": mode}]
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
    except Exception as e:
        print("❌ Ошибка установки режима ИИ:", e)

# 🧠 Очистить режим ИИ
def clear_ai_mode(chat_id: int):
    url = f"{SUPABASE_URL}/rest/v1/user_settings?chat_id=eq.{chat_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print("❌ Ошибка удаления режима ИИ:", e)
