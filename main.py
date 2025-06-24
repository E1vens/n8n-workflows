from fastapi import FastAPI, Request
from utils.embeddings import get_embedding
from utils.supabase import match_documents
from handlers.buttons import get_reply_markup
from config import TELEGRAM_TOKEN, TELEGRAM_API_URL
import httpx

app = FastAPI()

# 📤 Отправка сообщения в Telegram
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

# 📬 Основной webhook
@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    message = data.get("message") or data.get("callback_query")
    chat_id = message["chat"]["id"] if "chat" in message else message["from"]["id"]
    text = message.get("text") or message.get("data") or ""

    # ✅ Обработка выбора категории через callback
    if text.startswith("category:"):
        category = text.replace("category:", "")
        results = await match_documents(category=category)

        if not results:
            return await send_message(chat_id, f"В категории *{category}* ничего не найдено.")

        reply = "\n\n".join([
            f"**{item['metadata']['title']}**\n"
            f"Цена: {item['metadata']['price']}₽ • "
            f"Объём: {item['metadata']['volume']} • "
            f"Крепость: {item['metadata']['strength']}\n"
            f"🔗 [Ссылка на товар]({item['metadata']['product_url']})"
            for item in results[:10]
        ])
        if len(results) > 10:
            reply += f"\n\n_Pоказано 10 из {len(results)} результатов._"

        return await send_message(chat_id, reply)

    # ✅ Команда /start
    if text.lower() in ["/start", "старт"]:
        return await send_message(chat_id, "Добро пожаловать! Выберите категорию:", get_reply_markup())

    # ✅ Обычный текстовый запрос с эмбеддингом
    embed = await get_embedding(text)
    results = await match_documents(embed)

    if not results:
        return await send_message(chat_id, "К сожалению, ничего не найдено по вашему запросу. Попробуйте изменить категорию или уточнить цену.")

    reply = "\n\n".join([
        f"**{item['metadata']['title']}**\n"
        f"Цена: {item['metadata']['price']}₽ • "
        f"Объём: {item['metadata']['volume']} • "
        f"Крепость: {item['metadata']['strength']}\n"
        f"🔗 [Ссылка на товар]({item['metadata']['product_url']})"
        for item in results[:10]
    ])
    if len(results) > 10:
        reply += f"\n\n_Pоказано 10 из {len(results)} результатов. Напишите, если хотите увидеть больше._"

    return await send_message(chat_id, reply)

