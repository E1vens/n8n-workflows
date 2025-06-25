import requests
import json
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_RPC_FUNCTION

def match_documents_by_category(category: str) -> list:
    url = f"{SUPABASE_URL}/rest/v1/documents"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    params = {
        "select": "*",
        "metadata->>category": f"eq.{category}",
        "limit": 10
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("❌ Supabase category error:", response.status_code, response.text)
        return []
