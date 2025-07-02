from fastapi import FastAPI, Request
from config import TELEGRAM_API_URL
from handlers.commands import handle_text_message
from handlers.callbacks import handle_callback_query
from handlers.age import is_confirmed, handle_age_confirmation, request_age_confirmation
from fastapi.concurrency import run_in_threadpool
import httpx
import json
import traceback
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = FastAPI()


# --- Отправка сообщений в Telegram ---
async def send_message(chat_id: int, text: str, reply_markup: dict | None = None, photo: str | None = None):
    payload = {"chat_id": chat_id}

    if photo:
        payload.update({"photo": photo, "caption": text})
        method = "sendPhoto"
    else:
        payload["text"] = text
        if reply_markup:
            payload["reply_markup"] = reply_markup
        method = "sendMessage"

    logging.info("Payload: %s", json.dumps(payload, indent=2, ensure_ascii=False))

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{TELEGRAM_API_URL}/{method}", json=payload)
        logging.info("Ответ Telegram: %s %s", response.status_code, response.content.decode())

@app.post("/webhook")
async def telegram_webhook(req: Request):
    logging.info("📥 Получен запрос от Telegram")
    try:
        data = await req.json()
        logging.info("📦 Данные от Telegram: %s", json.dumps(data, indent=2, ensure_ascii=False))

        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "").strip()

            if not text:
                return {"ok": True}

            if not is_confirmed(chat_id):
                if text.startswith("age:"):
                    result = handle_age_confirmation(chat_id, text)
                    return await send_message(chat_id, result["text"], reply_markup=result.get("reply_markup"))
                return await send_message(chat_id, **request_age_confirmation(chat_id))

            return await handle_text_message(chat_id, text, send_message)

        elif "callback_query" in data:
            return await handle_callback_query(data["callback_query"], send_message, get_ai_stop_keyboard)

        return {"ok": True}

    except Exception as e:
        logging.exception("❌ Глобальная ошибка:")
        return {"ok": True}
