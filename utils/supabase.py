import requests
from config import SUPABASE_URL, SUPABASE_KEY

def match_documents_by_category(category: str, sort: str = "asc", page: int = 1, per_page: int = 10) -> list:
    url = f"{SUPABASE_URL}/rest/v1/documents"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Range-Unit": "items",
        "Range": f"{(page - 1) * per_page}-{(page * per_page) - 1}"
    }

    # Внимание: фильтруем по вложенному полю metadata->>category
    params = {
        "select": "*",
        "metadata->>category": f"eq.{category}",
        "order": f"metadata->>title.{sort}"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("\u274c Supabase category error:", str(e))
        print("\ud83d\udce6 Ответ Supabase:", response.text)
        return []

# Заглушка для текстового поиска (эмбеддингов)
async def match_documents(embedding: list) -> list:
    print("\u26a0\ufe0f Заглушка match_documents вызвана")
    return []
