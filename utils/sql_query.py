import requests
import json
from config import SUPABASE_URL, SUPABASE_KEY

def run_sql_query(sql: str) -> list:
    url = f"{SUPABASE_URL}/rest/v1/rpc/execute_sql"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "sql": sql
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json()
    else:
        print("❌ Supabase SQL Error:", response.status_code, response.text)
        return []
