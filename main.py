from fastapi import FastAPI, Request
from config import TELEGRAM_API_URL
from handlers.commands import handle_text_message
from handlers.callbacks import handle_callback_query
from handlers.age import is_confirmed, handle_age_confirmation, request_age_confirmation
from fastapi.concurrency import run_in_threadpool
from handlers.buttons import get_main_menu
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
async def send_message(
    chat_id: int,
    text: str,
    reply_markup: dict | None = None,
    photo: str | None = None,
    use_markdown: bool = False  # 👈 добавляем флаг
):
    payload = {"chat_id": chat_id}

    if photo:
        payload.update({"photo": photo, "caption": text})
        if use_markdown:
            payload["parse_mode"] = "MarkdownV2"
        method = "sendPhoto"
    else:
        payload["text"] = text
        if use_markdown:
            payload["parse_mode"] = "Markdown"
        if reply_markup:
            payload["reply_markup"] = reply_markup
        method = "sendMessage"

    logging.info("Payload: %s", json.dumps(payload, indent=2, ensure_ascii=False))

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{TELEGRAM_API_URL}/{method}", json=payload)
        logging.info("Ответ Telegram: %s %s", response.status_code, response.content.decode())

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    try:
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")
            return await handle_text_message(chat_id, text, send_message)

        elif "callback_query" in data:
            callback = data["callback_query"]
            chat_id = callback["from"]["id"]
            data_value = callback.get("data", "")

            # 👉 Обработка кнопки "/stop"
            if data_value == "/stop":
                return await handle_text_message(chat_id, "/stop", send_message)

            return await handle_callback_query(chat_id, data_value, send_message, None)

        return {"ok": True}

    except Exception as e:
        logging.exception("❌ Глобальная ошибка:")
        return {"ok": True}
