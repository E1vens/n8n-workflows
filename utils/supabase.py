import requests
import json
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_RPC_FUNCTION

def match_documents(embedding, match_count=5, filter={}) -> list:
    url = f"{SUPABASE_URL}/rest/v1/rpc/{SUPABASE_RPC_FUNCTION}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "query_embedding": embedding,
        "match_count": match_count,
        "filter": filter
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json()
    else:
        print("❌ Supabase error:", response.status_code, response.text)
        return []
