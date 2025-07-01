import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

async def get_embedding(text: str) -> list[float]:
    response = openai.Embedding.create(
        model="text-embedding-3-small",
        input=text
    )
    return response['data'][0]['embedding']


### ✅ FILE: utils/supabase.py (добавить функции для работы с режимами и векторным поиском)
import os
import requests

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_APIKEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}


def set_ai_mode(chat_id: int, mode: str):
    payload = [{"chat_id": chat_id, "ai_mode": mode}]
    url = f"{SUPABASE_URL}/rest/v1/user_settings"
    requests.post(url, headers=HEADERS, json=payload)


def get_ai_mode(chat_id: int) -> str | None:
    url = f"{SUPABASE_URL}/rest/v1/user_settings?select=ai_mode&chat_id=eq.{chat_id}"
    resp = requests.get(url, headers=HEADERS)
    if resp.ok and resp.json():
        return resp.json()[0]["ai_mode"]
    return None


def clear_ai_mode(chat_id: int):
    url = f"{SUPABASE_URL}/rest/v1/user_settings?chat_id=eq.{chat_id}"
    requests.delete(url, headers=HEADERS)


def call_match_documents(embedding: list[float], top_k: int = 5):
    url = f"{SUPABASE_URL}/rest/v1/rpc/match_documents"
    payload = {
        "query_embedding": embedding,
        "match_count": top_k
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    return resp.json() if resp.ok else []

