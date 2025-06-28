from fastapi import FastAPI, Request
from handlers.catalog import handle_catalog_overview, handle_category_selection
from config import TELEGRAM_API_URL
from urllib.parse import unquote
import httpx

app = FastAPI()

async def send_message(chat_id: int, text: str, reply_markup: dict | None = None, photo: str | None = None):
    payload = {
        "chat_id": chat_id,
        "parse_mode": "Markdown"
    }
    if photo:
        payload.update({"photo": photo, "caption": text})
        method = "sendPhoto"
    else:
        payload["text"] = text
        if reply_markup:
            payload["reply_markup"] = reply_markup
        method = "sendMessage"

    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API_URL}/{method}", json=payload)

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    chat_id = None
    text = ""

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").strip()

        if text == "🛍 Каталог":
            return await handle_catalog_overview(chat_id, send_message)

        return await send_message(chat_id, "Нажмите 🛍 Каталог")

    elif "callback_query" in data:
        chat_id = data["callback_query"]["from"]["id"]
        text = data["callback_query"].get("data", "").strip()

        if text.startswith("category|"):
            try:
                _, raw_category, page = text.split("|")
                category = unquote(raw_category)
                return await handle_category_selection(chat_id, category, send_message, int(page))
            except Exception as e:
                print("❌ Ошибка обработки category callback:", e)
                return await send_message(chat_id, "⚠️ Не удалось загрузить товары.")

    return {"ok": True}
