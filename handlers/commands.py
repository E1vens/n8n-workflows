from handlers.age import is_confirmed, request_age_confirmation, handle_age_confirmation
from handlers.language import get_translated_text, get_main_menu
from handlers.loyalty import register_loyalty_card
from handlers.catalog import handle_catalog_overview
from handlers.elite import handle_elite
from handlers.info import handle_info
from handlers.ai import handle_text_message_ai, clear_ai_mode, get_ai_mode
from fastapi.concurrency import run_in_threadpool


async def handle_text_message(chat_id, text, send_message):
    text = text.strip()

    # --- Проверка возраста ---
    if not is_confirmed(chat_id):
        if text.startswith("age:"):
            result = handle_age_confirmation(chat_id, text)
            return await send_message(
                chat_id,
                text=result["text"],
                reply_markup=result.get("reply_markup")
            )
        return await send_message(chat_id, **request_age_confirmation(chat_id))

    # --- /stop ---
    if text.lower() == "/stop":
        clear_ai_mode(chat_id)
        return await send_message(chat_id, "🛑 ИИ-режим завершён.", reply_markup=get_main_menu(chat_id))

    # --- Если ИИ активен ---
    ai_mode = get_ai_mode(chat_id)
    if ai_mode:
        reply = await handle_text_message_ai(chat_id, text)
        if reply:
            return await send_message(chat_id, reply)
        return await send_message(
            chat_id,
            "⚠️ Чтобы использовать эту функцию, сначала завершите диалог с ИИ.\n\nНапишите `/stop`."
        )

    # --- /start ---
    if text.lower() == "/start":
        await register_loyalty_card(chat_id)
        return await send_message(chat_id, get_translated_text(chat_id, "menu_prompt"), reply_markup=get_main_menu(chat_id))

    # --- ИИ консультант ---
    if text.lower() in ["🤖 ии консультант", "ии консультант", "ai assistant", "asistente ia"]:
        return await send_message(chat_id, "Напишите свой вопрос, и ИИ сам поймёт, чем помочь 🤖")

    # --- Каталог ---
    if text.lower() in ["каталог", "🛍 каталог"]:
        return await handle_catalog_overview(chat_id, send_message)

    # --- Элитный алкоголь ---
    if "элит" in text.lower():
        return await handle_elite(chat_id, send_message)

    # --- Информация о компании ---
    if "информация" in text.lower():
        return await handle_info(chat_id, send_message)

    # --- Карта лояльности ---
    if "карта" in text.lower() or "баланс" in text.lower():
        status, data = await run_in_threadpool(register_loyalty_card, chat_id)
        if status == "exists":
            tier = data.get("tier", "Bronze").capitalize()
            total_orders = data.get("total_orders", 0)
            return await send_message(chat_id,
                f"🎁 *Ваша карта лояльности:*

"
                f"• Уровень: `{tier}`
"
                f"• Заказов: `{total_orders}`
"
            )

    # --- По умолчанию ---
    return await send_message(chat_id, get_translated_text(chat_id, "menu_prompt"), reply_markup=get_main_menu(chat_id))
