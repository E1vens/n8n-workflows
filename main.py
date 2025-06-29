from fastapi import FastAPI, Request
from handlers.catalog import handle_catalog_overview, handle_category_selection
from handlers.buttons import get_main_menu
from config import TELEGRAM_API_URL
from urllib.parse import unquote
import httpx
import json

app = FastAPI()

# Отправка сообщения в Telegram
async def send_message(chat_id: int, text: str, reply_markup: dict | None = None, photo: str | None = None):
    payload = {
        "chat_id": chat_id,
        # "parse_mode": "Markdown"  # можно включить позже
    }

    if photo:
        payload.update({"photo": photo, "caption": text})
        method = "sendPhoto"
    else:
        payload["text"] = text
        if reply_markup:
            payload["reply_markup"] = reply_markup
        method = "sendMessage"

    print("📤 Payload:", json.dumps(payload, indent=2, ensure_ascii=False))

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{TELEGRAM_API_URL}/{method}", json=payload)
        print("📥 Ответ Telegram:", response.status_code, await response.text())

# Основной вебхук
@app.post("/webhook")
async def telegram_webhook(req: Request):
    print("📥 Получен запрос от Telegram")

    try:
        data = await req.json()
        print("📦 Данные:", json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print("❌ Ошибка чтения JSON:", e)
        return {"ok": True}

    chat_id = None
    text = ""

    # Обработка обычных сообщений
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text")

        if not text:
            print("📭 Пустое сообщение (возможно стикер, фото, и т.д.) — игнорируем")
            return {"ok": True}

        text = text.strip()
        print(f"📩 Сообщение от пользователя: {text}")

        if "каталог" in text.lower():
            return await handle_catalog_overview(chat_id, send_message)

        return await send_message(chat_id, "Нажмите 🛍 Каталог", reply_markup=get_main_menu())

    # Обработка inline-кнопок (callback_query)
    elif "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["from"]["id"]
        data_value = callback.get("data", "").strip()
        print(f"📲 Callback получен: {data_value}")

        if data_value.startswith("category|"):
            try:
                _, raw_category, page = data_value.split("|")
                category = unquote(raw_category)
                return await handle_category_selection(chat_id, category, send_message, int(page))
            except Exception as e:
                print("❌ Ошибка разбора callback 'category':", e)
                return await send_message(chat_id, "⚠️ Не удалось загрузить товары.")

    return {"ok": True}
