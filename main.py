from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from config import TELEGRAM_API_URL
from utils.sender import send_message
from handlers.age import handle_start, handle_age_confirmation, is_age_confirmed
from handlers.ai import is_ai_active, activate_ai, deactivate_ai
from handlers.catalog import handle_catalog, handle_category
from handlers.buttons import get_main_menu, get_ai_exit_button
from utils.embeddings import get_embedding
from utils.supabase import match_documents
import httpx
import re

app = FastAPI()

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

    # ✅ Обработка подтверждения возраста
    if text.startswith("age:"):
        return await handle_age_confirmation(chat_id, text)

    # ✅ Команда /start
    if text.lower() in ["/start", "старт"]:
        return await handle_start(chat_id)

    # ✅ Проверка возраста
    if not is_age_confirmed(chat_id):
        return await send_message(chat_id, "🚫 Доступ запрещён. Нажмите /start и подтвердите возраст.")

    # ✅ Обработка нижнего меню
    if text == "🛍 Каталог":
        return await handle_catalog(chat_id)

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

    # ✅ Обработка inline-кнопок категорий
    if text.startswith("category:"):
        return await handle_category(chat_id, text)

    # ✅ Поиск по эмбеддингу (ИИ-консультант)
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
