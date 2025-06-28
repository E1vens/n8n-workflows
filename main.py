from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from handlers.catalog import handle_catalog_overview, handle_category_selection
from config import TELEGRAM_API_URL
from urllib.parse import unquote
import httpx

print("✅ Минимальный main.py загружен")

app = FastAPI()

# 🔹 Отправка сообщения
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

# 🔹 Обработка запросов от Telegram
@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    chat_id = None
    text = ""

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()
        print(f"📩 Сообщение: {text}")

        if text == "🛍 Каталог":
            return await handle_catalog_overview(chat_id, send_message)  # << вот это ОБЯЗАТЕЛЬНО выше

        return await send_message(chat_id, "Нажмите 🛍 Каталог для теста.")  # << иначе всегда сюда

    elif "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["from"]["id"]
        text = callback.get("data", "").strip()
        print(f"📥 Callback: {text}")

        if text.startswith("category|"):
            try:
                _, raw_category, page = text.split("|")
                category = unquote(raw_category)
                return await handle_category_selection(chat_id, category, send_message, int(page))
            except Exception as e:
                print(f"❌ Ошибка разбора callback: {e}")
                return await send_message(chat_id, "⚠️ Ошибка обработки категории.")

        return await send_message(chat_id, "⚠️ Неизвестная команда в callback.")

    return {"ok": True}
