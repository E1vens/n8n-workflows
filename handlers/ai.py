import re
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
    set_ai_mode(chat_id, mode)
    return f"ИИ-помощник активирован в режиме: {mode}"

async def handle_text_message_ai(chat_id: int, message: str):
    mode = get_ai_mode(chat_id)
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

        # --- Извлекаем фильтры из текста ---
        price_match = re.search(r"до\s*(\d+)", message.lower())
        max_price = float(price_match.group(1)) if price_match else None

        strength_min_match = re.search(r"от\s*(\d+\.?\d*)\s*%", message.lower())
        strength_max_match = re.search(r"до\s*(\d+\.?\d*)\s*%", message.lower())
        min_strength = float(strength_min_match.group(1)) if strength_min_match else None
        max_strength = float(strength_max_match.group(1)) if strength_max_match else None

        results = call_match_documents(
            embedding,
            top_k=5,
            max_price=max_price,
            min_strength=min_strength,
            max_strength=max_strength
        )

        if not results:
            return "❌ Ничего не найдено. Попробуйте изменить запрос."

        msg = "\n\n".join([
            f"📦 *{r['title']}*\n"
            f"Цена: {r['price']}₽ • Объём: {r['volume']} • Крепость: {r['strength']}\n"
            f"[🔗 Ссылка на товар]({r['product_url']})"
            for r in results
        ])
        return msg

    return "⚠️ Неизвестный режим ИИ."
