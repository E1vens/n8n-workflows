from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from utils.supabase import get_distinct_categories
from config import TELEGRAM_API_URL
import httpx

print("✅ Минимальный main.py загружен")

app = FastAPI()

async def send_message(chat_id: int, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        })

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    chat_id = None
    text = ""

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()
    else:
        return {"ok": True}

    print(f"📩 Получено сообщение: {text}")

    if text == "🛍 Каталог":
        return await handle_catalog_overview(chat_id, send_message)
        if not categories:
            return await send_message(chat_id, "⚠️ Категории не найдены.")
        reply = "Категории:\n" + "\n".join(f"• {c}" for c in categories)
        return await send_message(chat_id, reply)

    return await send_message(chat_id, "Нажмите 🛍 Каталог для теста.")
