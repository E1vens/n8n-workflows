from fastapi import FastAPI, Request
from urllib.parse import unquote
from config import TELEGRAM_API_URL
from handlers.buttons import get_main_menu, get_category_buttons
import httpx

app = FastAPI()

async def send_message(chat_id: int, text: str, reply_markup: dict | None = None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    async with httpx.AsyncClient() as client:
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

        if text in ["/start", "старт"]:
            return await send_message(chat_id, "Нажмите 🛍 Каталог", get_main_menu())

        if text == "🛍 Каталог":
            return await send_message(chat_id, "Выберите категорию:", get_category_buttons())

        return await send_message(chat_id, "Нажмите 🛍 Каталог")

    elif "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["from"]["id"]
        text = callback.get("data", "").strip()

        if text.startswith("category|"):
            _, raw_category, _ = text.split("|")
            category = unquote(raw_category)
            return await send_message(chat_id, f"✅ Вы выбрали категорию: *{category}*")

    return {"ok": True}
