import requests
from config import SUPABASE_URL, SUPABASE_KEY

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

# Заглушка для поиска по эмбеддингам
async def match_documents(embedding: list) -> list:
    print("⚠️ Заглушка match_documents вызвана")
    return []
