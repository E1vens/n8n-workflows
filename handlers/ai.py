import re
from utils.supabase import get_ai_mode, set_ai_mode, clear_ai_mode, call_match_documents
from utils.embeddings import get_embedding
from utils.gpt import ask_gpt, detect_ai_mode_gpt  # ⬅️ GPT-анализ
from handlers.language import get_user_language
from handlers.faq import find_faq_answer, translate_if_needed


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
    mode = await detect_ai_mode_gpt(message)
    print(f"🤖 GPT определил режим: {mode}")
    set_ai_mode(chat_id, mode)
    if not mode:
        return None

    if mode == "chat":
        messages = [
            {"role": "system", "content": "Ты умный помощник, говори дружелюбно и кратко."},
            {"role": "user", "content": message}
        ]
        return await ask_gpt(messages)

    if mode == "faq":
        lang = get_user_language(chat_id) or "ru"
        answer_ru = find_faq_answer(message)

        if answer_ru:
            return await translate_if_needed(answer_ru, lang)

        messages = [
            {
                "role": "system",
                "content": "Ты консультант компании, рассказывай строго и уверенно, основываясь на предоставленной информации."
            },
            {"role": "user", "content": message}
        ]
        return await ask_gpt(messages)

    if mode == "search":
        embedding = await get_embedding(message)

        price_match = re.search(r"до\s*(\d+)", message.lower())
        max_price = float(price_match.group(1)) if price_match else None

        categories = {
            "вино": "вино",
            "водка": "водка",
            "шампанское": "шампанское",
            "ром": "ром",
            "коньяк": "коньяк",
            "виски": "виски",
            "текила": "текила",
        }

        detected_category = None
        for key in categories:
            if key in message.lower():
                detected_category = categories[key]
                break

        top_k = 10

        results = call_match_documents(
            embedding=embedding,
            top_k=top_k,
            max_price=max_price
        )

        if detected_category:
            results = [r for r in results if detected_category.lower() in r["title"].lower()]

        if not results:
            return "❌ Ничего не найдено по вашему запросу. Попробуйте изменить формулировку."

        msg = "\n\n".join([
            f"📦 *{r['title']}*\n"
            f"Цена: {r['price']}₽ • Объём: {r['volume']} • Крепость: {r['strength']}\n"
            f"[🔗 Ссылка на товар]({r['product_url']})"
            for r in results
        ])
        return msg

    return "⚠️ Неизвестный режим ИИ."
