from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from utils.supabase import get_distinct_categories
from handlers.catalog import handle_category_selection, handle_catalog_overview
from config import TELEGRAM_API_URL
from telegram import ReplyKeyboardMarkup, KeyboardButton
from urllib.parse import unquote
import httpx

print("✅ Минимальный main.py загружен")

app = FastAPI()

# 📩 Отправка сообщения
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

# 📦 Получение категорий
async def handle_catalog_overview(chat_id: int, send_message):
    categories = await run_in_threadpool(get_distinct_categories)
    if not categories:
        return await send_message(chat_id, "⚠️ Категории не найдены.")

    reply = "Категории:\n" + "\n".join(f"• {c}" for c in categories)
    return await send_message(chat_id, reply)

# 🧷 Главное меню
def get_main_menu():
    keyboard = [
        [KeyboardButton("🛍 Каталог")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True).to_dict()

# 📬 Вебхук
@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    chat_id = None
    text = ""

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()

    elif "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["from"]["id"]
        text = callback.get("data", "").strip()

        if text.startswith("category|"):
            _, raw_category, page = text.split("|")
            category = unquote(raw_category)
            return await handle_category_selection(chat_id, category, send_message, int(page))

        return await send_message(chat_id, "⚠️ Неизвестная команда.")

    else:
        return {"ok": True}

    print(f"📩 Получено сообщение: {text}")

    if text == "🛍 Каталог":
        return await handle_catalog_overview(chat_id, send_message)

    return await send_message(chat_id, "Нажмите 🛍 Каталог для теста.", get_main_menu())
