from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from handlers.age import handle_age_confirmation, is_confirmed, request_age_confirmation
from handlers.catalog import handle_catalog_overview
from handlers.buttons import get_age_confirmation_buttons, get_category_buttons
from utils.supabase import match_documents_by_category
from config import TELEGRAM_TOKEN, TELEGRAM_API_URL
import httpx

print("✅ main.py успешно загружен")

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
    try:
        data = await req.json()
    except Exception as e:
        print("❌ Ошибка чтения запроса:", e)
        return {"ok": False}

    chat_id = None
    text = ""

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()

    if not chat_id or not text:
        return await send_message(chat_id, "⚠️ Сообщение не распознано. Повторите ввод.")

    if text.startswith("age:"):
        result = handle_age_confirmation(chat_id, text)
        return await send_message(chat_id, result["text"], result.get("reply_markup"))

    if text.lower() in ["/start", "старт"]:
        return await send_message(chat_id, "Подтвердите, пожалуйста, что вам есть 18 лет:", get_age_confirmation_buttons())

    if not is_confirmed(chat_id):
        result = request_age_confirmation()
        return await send_message(chat_id, result["text"], result.get("reply_markup"))

    if text == "🛍 Каталог":
        return await handle_catalog_overview(chat_id, send_message)

    if text == "👑 Элитный алкоголь":
        results = await run_in_threadpool(match_documents_by_category, "Элитный", "desc", 1, 10)
        if not results:
            return await send_message(chat_id, "Элитный алкоголь не найден.")

        reply = "\n\n".join([
            f"*{item.get('title', 'Без названия')}*\n"
            f"Цена: {item.get('price', '?')}₽ • "
            f"Объём: {item.get('volume', '?')} • "
            f"Крепость: {item.get('strength', '?')}\n"
            f"🔗 [Ссылка на товар]({item.get('product_url', '#')})"
            for item in results
        ])
        return await send_message(chat_id, reply)

    return await send_message(chat_id, "К сожалению, ничего не найдено. Попробуйте другой запрос.")
