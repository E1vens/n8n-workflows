from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from handlers.catalog import handle_catalog_overview, handle_category_selection
from config import TELEGRAM_API_URL
from urllib.parse import unquote
import httpx

app = FastAPI()

async def send_message(chat_id: int, text: str, reply_markup: dict | None = None, photo: str | None = None):
    async with httpx.AsyncClient() as client:
        payload = {
            "chat_id": chat_id,
            "parse_mode": "Markdown"
        }
        if photo:
            payload.update({"photo": photo, "caption": text})
            await client.post(f"{TELEGRAM_API_URL}/sendPhoto", json=payload)
        else:
            payload.update({"text": text})
            if reply_markup:
                payload["reply_markup"] = reply_markup
            await client.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    chat_id = None
    text = ""

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()
        if text == "🛍 Каталог":
            return await handle_catalog_overview(chat_id, send_message)
        return await send_message(chat_id, "Нажмите 🛍 Каталог")

    elif "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["from"]["id"]
        text = callback.get("data", "").strip()
        if text.startswith("category|"):
            try:
                _, raw_category, page = text.split("|")
                category = unquote(raw_category)
                return await handle_category_selection(chat_id, category, send_message, int(page))
            except Exception as e:
                print("Ошибка callback:", e)
                return await send_message(chat_id, "⚠️ Ошибка обработки кнопки.")

    return {"ok": True}
