import re
import requests
from utils.supabase import get_ai_mode, set_ai_mode, clear_ai_mode, call_match_documents
from utils.embeddings import get_embedding
from utils.gpt import ask_gpt, detect_ai_mode_gpt  # ⮆️ GPT-анализ
from handlers.language import get_user_language
from handlers.faq import find_faq_answer, translate_if_needed
from config import SUPABASE_URL, SUPABASE_KEY

# 🔐 Функция для записи в chat_logs

def log_chat_message(chat_id: int, role: str, content: str, metadata: dict | None = None):
    url = f"{SUPABASE_URL}/rest/v1/chat_logs"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "session_id": str(chat_id),
        "user_id": str(chat_id),
        "role": role,
        "content": content,
        "metadata": metadata or {}
    }
    try:
        requests.post(url, headers=headers, json=[payload])
    except Exception as e:
        print("❌ Ошибка записи в chat_logs:", e)

# 🔎 Простая оперативная "память"
SEARCH_CONTEXT = {}  # chat_id: {category, max_price, embedding, page}

FOLLOW_UP_PHRASES = [
    "еще", "ещё", "что еще", "что-нибудь еще", "а еще", "а есть еще", "это все", "всё?"
]


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
    log_chat_message(chat_id, "user", message)

    mode = await detect_ai_mode_gpt(message)
    print(f"🤖 GPT определил режим: {mode}")

    if mode == "company":
        mode = "faq"

    set_ai_mode(chat_id, mode)

    if not mode:
        return None

    if mode == "chat":
        messages = [
            {"role": "system", "content": "Ты умный помощник, говори дружелюбно и кратко."},
            {"role": "user", "content": message}
        ]
        reply = await ask_gpt(messages)
        log_chat_message(chat_id, "assistant", reply, {"ai_mode": mode})
        return reply

    if mode == "faq":
        lang = get_user_language(chat_id) or "ru"
        answer_ru = find_faq_answer(message)

        if answer_ru:
            translated = await translate_if_needed(answer_ru, lang)
            log_chat_message(chat_id, "assistant", translated, {"ai_mode": mode})
            return translated

        messages = [
            {"role": "system", "content": "Ты консультант компании, рассказывай строго и уверенно."},
            {"role": "user", "content": message}
        ]
        reply = await ask_gpt(messages)
        log_chat_message(chat_id, "assistant", reply, {"ai_mode": mode})
        return reply

    if mode == "search":
        text = message.lower()
        is_follow_up = any(phrase in text for phrase in FOLLOW_UP_PHRASES)

        if is_follow_up and chat_id in SEARCH_CONTEXT:
            ctx = SEARCH_CONTEXT[chat_id]
            ctx["page"] += 1
            results = call_match_documents(
                embedding=ctx["embedding"],
                top_k=10,
                max_price=ctx.get("max_price")
            )
            detected_category = ctx.get("category")
        else:
            embedding = await get_embedding(message)
            price_match = re.search(r"\bдо\s*(\d+)", message)
            max_price = float(price_match.group(1)) if price_match else None

            categories = {
                "вино": "вино", "водка": "водка", "шампанское": "шампанское",
                "ром": "ром", "коньяк": "коньяк", "виски": "виски", "текила": "текила",
            }
            detected_category = None
            for key in categories:
                if key in text:
                    detected_category = categories[key]
                    break

            results = call_match_documents(
                embedding=embedding,
                top_k=10,
                max_price=max_price
            )

            SEARCH_CONTEXT[chat_id] = {
                "embedding": embedding,
                "category": detected_category,
                "max_price": max_price,
                "page": 1
            }

        if detected_category:
            results = [r for r in results if detected_category.lower() in r["title"].lower()]

        if not results:
            return "❌ Ничего не найдено по вашему запросу. Попробуйте изменить формулировку."

        msg = "\n\n".join([
            f"📦 *{r['title']}*\nЦена: {r['price']}₽ • Объём: {r['volume']} • Крепость: {r['strength']}\n[🔗 Ссылка на товар]({r['product_url']})"
            for r in results
        ])
        log_chat_message(chat_id, "assistant", msg, {
            "ai_mode": mode,
            "category": detected_category,
            "max_price": SEARCH_CONTEXT[chat_id].get("max_price")
        })
        return msg

    return "⚠️ Неизвестный режим ИИ."
