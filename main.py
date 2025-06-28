from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from handlers.age import handle_age_confirmation, is_confirmed, request_age_confirmation
from handlers.catalog import handle_catalog_overview, handle_category_selection
from handlers.buttons import get_main_menu, get_age_confirmation_buttons, get_category_buttons
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
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip().lower()

        if text == "/start" or text == "старт":
            return await send_message(chat_id, "Подтвердите, пожалуйста, что вам есть 18 лет:", get_age_confirmation_buttons())

        if not is_confirmed(chat_id):
            result = request_age_confirmation()
            return await send_message(chat_id, result["text"], result["reply_markup"])

        if text == "🛍 каталог":
            return await send_message(chat_id, "Выберите категорию товара:", get_category_buttons())

        return await send_message(chat_id, "Нажмите 🛍 Каталог", get_main_menu())

    elif "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["from"]["id"]
        text = callback.get("data", "").strip()

        if text.startswith("age:"):
            result = handle_age_confirmation(chat_id, text)
            return await send_message(chat_id, result["text"], result.get("reply_markup", get_main_menu()))

        if text.startswith("category|"):
            try:
                _, raw_category, page = text.split("|")
                category = unquote(raw_category)
                return await handle_category_selection(chat_id, category, send_message, int(page))
            except Exception as e:
                print("❌ Ошибка обработки категории:", e)
                return await send_message(chat_id, "⚠️ Ошибка обработки категории.")

    return {"ok": True}
