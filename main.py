from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from utils.embeddings import get_embedding
from utils.supabase import match_documents, match_documents_by_category
from handlers.buttons import get_reply_markup, get_age_confirmation_buttons
from config import TELEGRAM_TOKEN, TELEGRAM_API_URL
import httpx

print("✅ main.py успешно загружен")

app = FastAPI()
confirmed_users = set()

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

    # message или callback_query
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

    if not chat_id or not text:
        return await send_message(chat_id, "⚠️ Сообщение не распознано. Повторите ввод.")

    # ✅ Обработка inline-кнопок
    if text.startswith("age:"):
        if text == "age:yes":
            confirmed_users.add(chat_id)
            return await send_message(chat_id, "✅ Спасибо! Вот доступные категории:", get_reply_markup())
        else:
            return await send_message(chat_id, "🚫 К сожалению, доступ запрещён. Повторно введите /start, если вам уже исполнилось 18.")

    # ✅ Команда /start
    if text.lower() in ["/start", "старт"]:
        return await send_message(chat_id, "Подтвердите, пожалуйста, что вам есть 18 лет:", get_age_confirmation_buttons())

    # ✅ Если возраст не подтверждён
    if chat_id not in confirmed_users:
        return await send_message(chat_id, "🚫 Доступ запрещён. Нажмите /start и подтвердите возраст.")

    # ✅ Выбор категории
    if text.startswith("category:"):
        category = text.replace("category:", "")
        results = await run_in_threadpool(match_documents_by_category, category)

        if not results:
            return await send_message(chat_id, f"В категории *{category}* ничего не найдено.")

        reply = "\n\n".join([
            f"*{item.get('metadata', {}).get('title', 'Без названия')}*\n"
            f"Цена: {item.get('metadata', {}).get('price', '?')}₽ • "
            f"Объём: {item.get('metadata', {}).get('volume', '?')} • "
            f"Крепость: {item.get('metadata', {}).get('strength', '?')}\n"
            f"🔗 [Ссылка на товар]({item.get('metadata', {}).get('product_url', '#')})"
            for item in results
        ])

        return await send_message(chat_id, reply)

    # ✅ Текстовый запрос (эмбеддинг)
    embed = await get_embedding(text)
    results = await match_documents(embed)

    if not results:
        return await send_message(chat_id, "К сожалению, ничего не найдено. Попробуйте другой запрос.")

    reply = "\n\n".join([
        f"*{item['metadata'].get('title', 'Без названия')}*\n"
        f"Цена: {item['metadata'].get('price', '?')}₽ • "
        f"Объём: {item['metadata'].get('volume', '?')} • "
        f"Крепость: {item['metadata'].get('strength', '?')}\n"
        f"🔗 [Ссылка на товар]({item['metadata'].get('product_url', '#')})"
        for item in results[:10]
    ])

    if len(results) > 10:
        reply += f"\n\n_Показано 10 из {len(results)} результатов._"

    return await send_message(chat_id, reply)
