import requests
from config import SUPABASE_URL, SUPABASE_KEY

def match_documents_by_category(category: str) -> list:
    url = f"{SUPABASE_URL}/rest/v1/documents"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    params = {
        "select": "*",
        "category": f"eq.{category}",
        "limit": 10
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("❌ Supabase category error:", str(e))
        return []

# Заглушка для эмбеддингов — оставить без изменений
async def match_documents(embedding: list) -> list:
    print("⚠️ Заглушка match_documents вызвана")
    return []
