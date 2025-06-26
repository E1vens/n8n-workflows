from fastapi import FastAPI, Request
from config import TELEGRAM_API_URL
from fastapi.concurrency import run_in_threadpool
from utils.embeddings import get_embedding
from utils.supabase import match_documents
from handlers.ai import is_ai_active, activate_ai, deactivate_ai
from handlers.age import handle_age_confirmation, is_confirmed, get_age_keyboard
from handlers.catalog import handle_category_selection
from handlers.buttons import (
    get_main_menu,
    get_category_buttons,
    get_ai_exit_button
)
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
    elif "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["from"]["id"]
        text = callback.get("data", "").strip()
    else:
        return {"ok": True}

    # ✅ Обработка возраста
    if text.startswith("age:"):
        return await handle_age_confirmation(chat_id, text, send_message)

    if text.lower() in ["/start", "старт"]:
        return await send_message(chat_id, "Подтвердите, пожалуйста, что вам есть 18 лет:", get_age_keyboard())

    if not is_confirmed(chat_id):
        return await send_message(chat_id, "🚫 Доступ запрещён. Нажмите /start и подтвердите возраст.")

    # ✅ Обработка текстовых кнопок
    if text == "🏍 Каталог":
        return await send_message(chat_id, "Выберите категорию:", get_category_buttons())

    if text == "🤖 ИИ консультант":
        activate_ai(chat_id)
        return await send_message(chat_id, "ИИ-консультант активирован. Задай свой вопрос:", get_ai_exit_button())

    if text == "🔙 Выйти из ИИ":
        deactivate_ai(chat_id)
        return await send_message(chat_id, "ИИ-консультант отключён. Выберите действие из меню:", get_main_menu())

    if text == "ℹ️ Информация о товаре":
        return await send_message(chat_id, "Отправьте название товара — я найду описание и характеристики.")

    if text == "🌐 Выбрать язык":
        return await send_message(chat_id, "Язык пока только русский. Скоро добавим другие!")

    if text == "🎁 Карта лояльности":
        return await send_message(chat_id, "🔖 Карта лояльности доступна в магазине. Оформим при покупке.")

    if text.startswith("category:"):
        return await handle_category_selection(chat_id, text, send_message)

    # ✅ ИИ-поиск
    if not is_ai_active(chat_id):
        return {"ok": True}

    embed = await get_embedding(text)
    results = await match_documents(embed)

    if not results:
        return await send_message(chat_id, "Ничего не найдено. Попробуй переформулировать запрос.")

    reply = "\n\n".join([
        f"*{item['metadata'].get('title', 'Без названия')}*\n"
        f"Цена: {item['metadata'].get('price', '?')}₽ • "
        f"Объём: {item['metadata'].get('volume', '?')} • "
        f"Крепость: {item['metadata'].get('strength', '?')}\n"
        f"🔗 [Ссылка на товар]({item['metadata'].get('product_url', '#')})"
        for item in results[:10]
    ])

    return await send_message(chat_id, reply)
