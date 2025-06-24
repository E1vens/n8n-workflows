from fastapi import FastAPI, Request
from utils.embeddings import get_embedding
from utils.supabase import match_documents, match_documents_by_category
from handlers.buttons import get_reply_markup, get_age_confirmation_buttons
from config import TELEGRAM_TOKEN, TELEGRAM_API_URL
import httpx

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
    data = await req.json()

    # message или callback_query
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
    elif "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["from"]["id"]
        text = callback.get("data", "")
    else:
        return {"ok": True}

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
        results = match_documents_by_category(category)
        if not results:
            return await send_message(chat_id, f"В категории *{category}* ничего не найдено.")

        reply = "\n\n".join([
            f"*{item['title']}*\nЦена: {item['price']}₽ • Объём: {item['volume']} • Крепость: {item['strength']}\n🔗 [Ссылка на товар]({item['product_url']})"
            for item in results
        ])

        return await send_message(chat_id, reply)

    # ✅ Текстовый запрос (эмбеддинг)
    embed = await get_embedding(text)
    results = await match_documents(embed)

    if not results:
        return await send_message(chat_id, "К сожалению, ничего не найдено. Попробуйте другой запрос.")

    reply = "\n\n".join([
        f"*{item['metadata']['title']}*\nЦена: {item['metadata']['price']}₽ • Объём: {item['metadata']['volume']} • Крепость: {item['metadata']['strength']}\n🔗 [Ссылка на товар]({item['metadata']['product_url']})"
        for item in results[:10]
    ])
    if len(results) > 10:
        reply += f"\n\n_Показано 10 из {len(results)} результатов._"

    return await send_message(chat_id, reply)
