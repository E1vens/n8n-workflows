from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from utils.embeddings import get_embedding
from utils.supabase import match_documents, match_documents_by_category
from handlers.ai import is_ai_active, activate_ai, deactivate_ai
from handlers.buttons import (
    get_age_confirmation_buttons,
    get_main_menu,
    get_category_buttons,
    get_ai_exit_button
)
from config import TELEGRAM_API_URL
import httpx
import re

app = FastAPI()
confirmed_users = set()
active_ai_users = set()


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

    # ✅ Обработка подтверждения возраста
    if text.startswith("age:"):
        if text == "age:yes":
            confirmed_users.add(chat_id)
            await send_message(chat_id, "✅ Спасибо! Меню доступно:", get_main_menu())
        else:
            await send_message(chat_id, "🚫 Доступ запрещён. Повторите /start, если вам уже исполнилось 18.")
        return {"ok": True}

    # ✅ Команда /start
    if text.lower() in ["/start", "старт"]:
        return await send_message(chat_id, "Подтвердите, пожалуйста, что вам есть 18 лет:", get_age_confirmation_buttons())

    # ✅ Проверка возраста
    if chat_id not in confirmed_users:
        return await send_message(chat_id, "🚫 Доступ запрещён. Нажмите /start и подтвердите возраст.")

    # ✅ Обработка нижнего меню
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

    # ✅ Обработка inline-кнопок категорий
    if text.startswith("category:"):
        match = re.match(r"category:(?P<cat>[^&]+)(?:&page=(?P<page>\\d+))?", text)
        if not match:
            return await send_message(chat_id, "⚠️ Неверный формат категории.")
        category = match.group("cat")
        page = int(match.group("page") or 1)

        results = await run_in_threadpool(match_documents_by_category, category, "asc", page, 10)
        if not results:
            return await send_message(chat_id, f"В категории *{category}* ничего не найдено.")

        reply = "\n\n".join([
            f"*{item.get('title', 'Без названия')}*\n"
            f"Цена: {item.get('price', '?')}\u20bd • "
            f"Объём: {item.get('volume', '?')} • "
            f"Крепость: {item.get('strength', '?')}\n"
            f"🔗 [Ссылка на товар]({item.get('product_url', '#')})"
            for item in results
        ])

        next_page_btn = {
            "inline_keyboard": [[{
                "text": "➡️ Следующая страница",
                "callback_data": f"category:{category}&page={page + 1}"
            }]]
        }

        return await send_message(chat_id, reply, next_page_btn)

    # ✅ Поиск по эмбеддингу (ИИ-консультант)
    if not is_ai_active(chat_id):
        return {"ok": True}

    embed = await get_embedding(text)
    results = await match_documents(embed)

    if not results:
        return await send_message(chat_id, "Ничего не найдено. Попробуй переформулировать запрос.")

    reply = "\n\n".join([
        f"*{item['metadata'].get('title', 'Без названия')}*\n"
        f"Цена: {item['metadata'].get('price', '?')}\u20bd • "
        f"Объём: {item['metadata'].get('volume', '?')} • "
        f"Крепость: {item['metadata'].get('strength', '?')}\n"
        f"🔗 [Ссылка на товар]({item['metadata'].get('product_url', '#')})"
        for item in results[:10]
    ])

    return await send_message(chat_id, reply)
