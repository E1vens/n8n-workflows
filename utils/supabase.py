import requests
from datetime import datetime
from config import SUPABASE_URL, SUPABASE_KEY

# 📦 Получение уникальных категорий
def get_distinct_categories():
    url = f"{SUPABASE_URL}/rest/v1/documents?select=category"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        raw_categories = [item.get("category") for item in response.json()]
        categories = sorted(set(filter(None, raw_categories)))
        return categories
    except Exception as e:
        print("❌ Ошибка получения категорий:", e)
        return []

# 📦 Уникальные товары по категории (с фильтрацией по title)
def get_top_products_by_category(category: str, limit: int = 5):
    url = f"{SUPABASE_URL}/rest/v1/documents"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Range": f"0-99",
        "Range-Unit": "items"
    }

    params = {
        "select": "title,price,volume,strength,metadata->>url,metadata->>photo",
        "category": f"eq.{category}",
        "order": "price.asc"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        all_items = response.json()

        seen_titles = set()
        unique_items = []
        for item in all_items:
            title = item.get("title")
            if title and title not in seen_titles:
                unique_items.append(item)
                seen_titles.add(title)
            if len(unique_items) >= limit:
                break

        return unique_items
    except Exception as e:
        print(f"❌ Ошибка получения товаров по категории '{category}':", e)
        return []

# 📦 Товары по категории (с постраничной навигацией)
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
        "category": f"eq.{category}",
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

# 🔍 Заглушка для поиска по эмбеддингам (до подключения n8n)
async def match_documents(embedding: list) -> list:
    print("⚠️ Заглушка match_documents вызвана")
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

    # Регистрация новой карты
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
def get_loyalty_card(chat_id: int) -> dict | None:
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
