from fastapi import FastAPI, Request
from utils.embeddings import get_embedding
from utils.supabase import match_documents
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
    message = data.get("message") or data.get("callback_query")
    chat_id = message["chat"]["id"] if "chat" in message else message["from"]["id"]
    text = message.get("text") or message.get("data") or ""

    # ✅ Проверка возраста (ответ на inline-кнопку)
    if text.startswith("age:"):
        if text == "age:yes":
            confirmed_users.add(chat_id)
            return await send_message(chat_id, "✅ Спасибо Большое! Вот доступные категории:", get_reply_markup())
        else:
            return await send_message(chat_id, "🚫 К сожалению, доступ запрещён. Повторно введите /start, если вам уже исполнилось 18.")

    # ✅ Старт команды: предлагаем подтвердить возраст
    if text.lower() in ["/start", "старт"]:
        return await send_message(chat_id, "Подтвердите, пожалуйста, что вам есть 18 лет:", get_age_confirmation_buttons())

    # ✅ Если пользователь не подтвердил возраст — блокируем доступ
    if chat_id not in confirmed_users:
        return await send_message(chat_id, "🚫 Доступ запрещён. Нажмите /start и подтвердите возраст.")

    # ✅ Обработка выбора категории
    if text.startswith("category:"):
        category = text.replace("category:", "")
        results = await match_documents(category=category)
        if not results:
            return await send_message(chat_id, f"В категории *{category}* ничего не найдено.")

        reply = "\n\n".join([
            f"**{item['metadata']['title']}**\nЦена: {item['metadata']['price']}₽ • Объём: {item['metadata']['volume']} • Крепость: {item['metadata']['strength']}\n🔗 [Ссылка на товар]({item['metadata']['product_url']})"
            for item in results[:10]
        ])
        if len(results) > 10:
            reply += f"\n\n_Pоказано 10 из {len(results)} результатов._"

        return await send_message(chat_id, reply)

    # ✅ Текстовый запрос — эмбеддинг
    embed = await get_embedding(text)
    results = await match_documents(embed)

    if not results:
        return await send_message(chat_id, "К сожалению, ничего не найдено. Попробуйте другой запрос.")

    reply = "\n\n".join([
        f"**{item['metadata']['title']}**\nЦена: {item['metadata']['price']}₽ • Объём: {item['metadata']['volume']} • Крепость: {item['metadata']['strength']}\n🔗 [Ссылка на товар]({item['metadata']['product_url']})"
        for item in results[:10]
    ])
    if len(results) > 10:
        reply += f"\n\n_Pоказано 10 из {len(results)} результатов._"

    return await send_message(chat_id, reply)
