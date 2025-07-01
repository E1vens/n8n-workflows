### ✅ FILE: utils/embeddings.py
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

async def get_embedding(text: str) -> list[float]:
    response = openai.Embedding.create(
        model="text-embedding-3-small",
        input=text
    )
    return response['data'][0]['embedding']


### ✅ FILE: utils/supabase.py (добавить функции для работы с режимами и векторным поиском)
import os
from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_APIKEY")
supabase = create_client(url, key)

async def set_ai_mode(chat_id: int, mode: str):
    supabase.table("user_settings").upsert({"chat_id": chat_id, "ai_mode": mode}).execute()

async def get_ai_mode(chat_id: int) -> str | None:
    result = supabase.table("user_settings").select("ai_mode").eq("chat_id", chat_id).execute()
    if result.data:
        return result.data[0]["ai_mode"]
    return None

async def clear_ai_mode(chat_id: int):
    supabase.table("user_settings").delete().eq("chat_id", chat_id).execute()

async def call_match_documents(embedding: list[float], top_k: int = 5):
    response = supabase.rpc("match_documents", {
        "query_embedding": embedding,
        "match_count": top_k
    }).execute()
    return response.data


### ✅ FILE: utils/gpt.py
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

async def ask_gpt(messages: list[dict], model="gpt-3.5-turbo") -> str:
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content


### ✅ FILE: handlers/ai.py
from utils.supabase import get_ai_mode, set_ai_mode, clear_ai_mode, call_match_documents
from utils.embeddings import get_embedding
from utils.gpt import ask_gpt

async def enable_ai_assistant(chat_id, send_message):
    reply_markup = {
        "inline_keyboard": [
            [{"text": "🔍 Поиск товаров", "callback_data": "ai_mode:search"}],
            [{"text": "💬 Живой чат", "callback_data": "ai_mode:chat"}],
            [{"text": "❓ Вопрос про компанию", "callback_data": "ai_mode:faq"}]
        ]
    }
    await send_message(chat_id, "Выберите режим работы ИИ:", reply_markup)

async def handle_ai_mode_selection(chat_id, mode):
    await set_ai_mode(chat_id, mode)
    return f"ИИ-помощник активирован в режиме: {mode}"

async def handle_text_message_ai(chat_id: int, message: str):
    mode = await get_ai_mode(chat_id)
    if not mode:
        return None

    if mode == "chat":
        messages = [
            {"role": "system", "content": "Ты умный помощник, говори дружелюбно и кратко."},
            {"role": "user", "content": message}
        ]
        return await ask_gpt(messages)

    if mode == "faq":
        messages = [
            {"role": "system", "content": "Ты консультант компании по алкоголю. Отвечай строго по теме."},
            {"role": "user", "content": message}
        ]
        return await ask_gpt(messages)

    if mode == "search":
        embedding = await get_embedding(message)
        results = await call_match_documents(embedding)
        if not results:
            return "Ничего не найдено. Попробуйте изменить запрос."

        msg = "\n\n".join([
            f"📦 *{r['title']}*\nЦена: {r['price']}₽ • Объём: {r['volume']} • Крепость: {r['strength']}\n[🔗 Ссылка на товар]({r['product_url']})"
            for r in results
        ])
        return msg

    return "Неверный режим. Используйте /stop для сброса."
