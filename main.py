from fastapi import FastAPI, Request
from handlers.catalog import handle_catalog_overview, handle_category_selection
from handlers.buttons import get_main_menu
from handlers.age import is_confirmed, request_age_confirmation, handle_age_confirmation
from handlers.info import handle_info
from config import TELEGRAM_API_URL
from urllib.parse import unquote
import httpx
import json
import traceback

app = FastAPI()

# ✅ Отправка сообщений в Telegram
async def send_message(chat_id: int, text: str, reply_markup: dict | None = None, photo: str | None = None):
    payload = {
        "chat_id": chat_id,
        # "parse_mode": "Markdown"  # можно включить при необходимости
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
        print("📥 Ответ Telegram:", response.status_code, response.content.decode())


# ✅ Обработка входящих сообщений и нажатий кнопок
@app.post("/webhook")
async def telegram_webhook(req: Request):
    print("📥 Получен запрос от Telegram")

    try:
        data = await req.json()
        print("📦 Данные:", json.dumps(data, indent=2, ensure_ascii=False))

        chat_id = None
        text = ""

        # 👉 Обычное сообщение от пользователя
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text")

            if not text:
                print("📭 Пустое сообщение (возможно стикер, фото и т.п.) — игнорируем")
                return {"ok": True}

            text = text.strip()
            print(f"📩 Сообщение от пользователя: {text}")

            if text.lower() in [
                "ℹ️ информация", "информация", "о компании",
                "ℹ️ информация о компании и партнёрах"
            ]:
                return await handle_info(chat_id, send_message)

            # 🔞 Проверка подтверждения возраста
            if not is_confirmed(chat_id):
                if text.startswith("age:"):
                    result = handle_age_confirmation(chat_id, text)
                    return await send_message(chat_id, result["text"], reply_markup=result.get("reply_markup"))
                return await send_message(chat_id, **request_age_confirmation())

            # ✅ Возраст подтверждён — продолжаем
            if text.lower() in ["/start", "каталог", "🛍 каталог"]:
                return await handle_catalog_overview(chat_id, send_message)

            return await send_message(chat_id, "Нажмите 🛍 Каталог", reply_markup=get_main_menu())


        # 👉 Callback от inline-кнопки
        elif "callback_query" in data:
            callback = data["callback_query"]
            chat_id = callback["from"]["id"]
            data_value = callback.get("data", "").strip()
            print(f"📲 Callback получен: {data_value}")

            # 🔞 Обработка подтверждения возраста
            if data_value.startswith("age:"):
                result = handle_age_confirmation(chat_id, data_value)
                return await send_message(chat_id, result["text"], reply_markup=result.get("reply_markup"))

            # 👉 Выбор категории
            if data_value.startswith("cat|"):
                try:
                    _, cat_id, page = data_value.split("|")
                    return await handle_category_selection(chat_id, cat_id, send_message, int(page))
                except Exception as e:
                    print("❌ Ошибка разбора callback 'cat|...':", e)
                    return await send_message(chat_id, "⚠️ Не удалось загрузить товары.")

        return {"ok": True}

    except Exception as e:
        print("❌ ГЛОБАЛЬНАЯ ОШИБКА:", str(e))
        traceback.print_exc()
        return {"ok": True}
