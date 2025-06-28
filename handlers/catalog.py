from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
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

    # Обработка обычного сообщения
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()
        print(f"📩 Сообщение: {text}")

        if text == "🛍 Каталог":
            return await handle_catalog_overview(chat_id, send_message)

        return await send_message(chat_id, "Нажмите 🛍 Каталог для теста.")

    # Обработка нажатий на кнопки (callback_query)
    elif "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["from"]["id"]
        text = callback.get("data", "").strip()
        print(f"📥 Callback: {text}")

        if text.startswith("category|"):
            try:
                _, raw_category, page = text.split("|")
                category = unquote(raw_category)
                return await send_message(chat_id, f"✅ Вы выбрали категорию: *{category}* (страница {page})")
            except Exception as e:
                print(f"❌ Ошибка разбора callback: {e}")
                return await send_message(chat_id, "⚠️ Ошибка обработки категории.")

        return await send_message(chat_id, "⚠️ Неизвестная команда в callback.")

    # Остальные случаи
    return {"ok": True}
