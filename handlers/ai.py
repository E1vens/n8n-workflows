import re
from utils.supabase import get_ai_mode, set_ai_mode, clear_ai_mode, call_match_documents
from utils.embeddings import get_embedding
from utils.gpt import ask_gpt, detect_ai_mode_gpt
from handlers.language import get_user_language
from utils.formatting import escape_markdown
from handlers.faq import find_faq_answer, translate_if_needed
from fastapi.concurrency import run_in_threadpool


# Простая оперативная "память" на время запроса (можно заменить на Supabase-хранилище при необходимости)
SEARCH_CONTEXT = {}  # chat_id: {category, max_price, embedding, page, top_k}

FOLLOW_UP_PHRASES = [
    "еще", "ещё", "что еще", "что-нибудь еще", "а еще", "а есть еще", "это все", "всё?"
]


async def handle_text_message_ai(chat_id: int, message: str, send_message):
    mode = get_ai_mode(chat_id)

    IGNORED_FOR_AI = [
        "🤖 ии консультант", "ии консультант", "ai assistant", "asistente ia",
        "каталог", "🛍 каталог",
        "🌐 выбрать язык", "выбрать язык",
        "ℹ️ информация о компании и партнёрах", "информация о компании",
        "карта лояльности", "🎁 карта лояльности",
        "баланс", "статистика", "/start", "/stop"
    ]
    if message.strip().lower() in IGNORED_FOR_AI:
        return None

    if not mode or mode == "detect":
        lowered = message.lower()
        if any(x in lowered for x in ["водка", "вино", "виски", "до", "за", "р", "₽", "крепость", "объём", "покажи", "каталог"]):
            mode = "search"
        elif any(x in lowered for x in ["что ты умеешь", "кто ты", "привет", "ку", "как дела"]):
            mode = "chat"
        else:
            mode = await detect_ai_mode_gpt(message)

    print(f"🤖 Режим ИИ определён как: {mode}")
    set_ai_mode(chat_id, mode)

        if mode == "company":
            mode = "faq"

        set_ai_mode(chat_id, mode)

    if not mode:
        messages = [
            {"role": "system", "content": "Ты умный помощник. Отвечай дружелюбно и понятно."},
            {"role": "user", "content": message}
        ]
        response = await ask_gpt(messages)
        escaped = escape_markdown(response)
        return await send_message(chat_id, escaped, use_markdown=True)

    if mode == "chat":
        messages = [
            {"role": "system", "content": "Ты умный помощник, говори дружелюбно и кратко."},
            {"role": "user", "content": message}
        ]
        response = await ask_gpt(messages)
        escaped = escape_markdown(response)
        return await send_message(chat_id, escaped, use_markdown=True)

    if mode == "faq":
        lang = get_user_language(chat_id) or "ru"
        answer_ru = find_faq_answer(message)

        if answer_ru:
            return await translate_if_needed(answer_ru, lang)

        messages = [
            {"role": "system", "content": "Ты консультант компании, рассказывай строго и уверенно."},
            {"role": "user", "content": message}
        ]
        response = await ask_gpt(messages)
        escaped = escape_markdown(response)
        return await send_message(chat_id, escaped, use_markdown=True)

    if mode == "search":
        text = message.lower()
        is_follow_up = any(phrase in text for phrase in FOLLOW_UP_PHRASES)

        if is_follow_up and chat_id in SEARCH_CONTEXT:
            ctx = SEARCH_CONTEXT[chat_id]
            ctx["page"] += 1
            results = await run_in_threadpool(
                call_match_documents,
                embedding=ctx["embedding"],
                top_k=ctx.get("top_k", 5),
                max_price=ctx.get("max_price")
            )
            detected_category = ctx.get("category")
        else:
            embedding = await get_embedding(message)

            price_match = re.search(r"до\s*(\d+)", message)
            max_price = float(price_match.group(1)) if price_match else None

            top_k_match = re.search(r"(\d+)\s+(?:лучших|топ|лучшие)", message)
            top_k = int(top_k_match.group(1)) if top_k_match else 5

            categories = {
                "вино": "вино", "водка": "водка", "шампанское": "шампанское",
                "ром": "ром", "коньяк": "коньяк", "виски": "виски", "текила": "текила",
            }
            detected_category = None
            for key in categories:
                if key in text:
                    detected_category = categories[key]
                    break

            results = await run_in_threadpool(
                call_match_documents,
                embedding=embedding,
                top_k=top_k,
                max_price=max_price
            )

            SEARCH_CONTEXT[chat_id] = {
                "embedding": embedding,
                "category": detected_category,
                "max_price": max_price,
                "page": 1,
                "top_k": top_k
            }

        if detected_category:
            results = [r for r in results if detected_category.lower() in r["title"].lower()]

        if not results:
            return await send_message(chat_id, "❌ Ничего не найдено по вашему запросу. Попробуйте изменить формулировку.")

        for r in results:
            title = escape_markdown(r['title'])
            url = escape_markdown(r['product_url'])
            price = escape_markdown(str(r['price']))
            volume = escape_markdown(r['volume'])
            strength = escape_markdown(r['strength'])
            is_sample = " \\(маленький образец\\)" if volume == "0.05 л" else ""

            msg = (
                f"[📦 {title}]({url})\n"
                f"Цена: {price}₽ • Объём: {volume}{is_sample} • Крепость: {strength}"
            )

            await send_message(chat_id, msg, use_markdown=True)

        return

    return None
