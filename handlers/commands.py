from handlers.catalog import handle_catalog_overview
from handlers.buttons import get_main_menu
from handlers.age import is_confirmed, request_age_confirmation, handle_age_confirmation
from handlers.info import handle_info
from handlers.elite import handle_elite
from handlers.language import handle_language_selection, get_translated_text
from handlers.loyalty import register_loyalty_card
from handlers.ai import (
    set_ai_mode,
    get_ai_mode,
    clear_ai_mode,
    handle_text_message_ai,
)
from fastapi.concurrency import run_in_threadpool


async def handle_text_message(chat_id: int, text: str, send_message):
    # --- Проверка возраста ---
    if not is_confirmed(chat_id):
        if text.startswith("age:"):
            result = handle_age_confirmation(chat_id, text)
            return await send_message(
                chat_id,
                result["text"],
                reply_markup=result.get("reply_markup")
            )
        return await send_message(
            chat_id,
            **request_age_confirmation(chat_id)
        )

    # --- /stop ---
    if text.lower() == "/stop":
        clear_ai_mode(chat_id)
        return await send_message(chat_id, "🛑 ИИ-режим завершён.", reply_markup=get_main_menu(chat_id))

    # --- Если ИИ активен ---
    ai_mode = get_ai_mode(chat_id)
    if ai_mode:
        reply = await handle_text_message_ai(chat_id, text, send_message)

        if reply is not None:
            return await send_message(chat_id, reply, use_markdown=True)

        # Если ответ пустой (None) → значит, фраза из списка игнорируемых
        return await send_message(
            chat_id,
            "⚠️ Чтобы использовать эту функцию, сначала завершите диалог с ИИ.\n\nНапишите /stop"
        )
  
    # --- ИИ консультант ---
    if text.lower() in ["🤖 ии консультант", "ии консультант", "ai assistant", "asistente ia"]:
        set_ai_mode(chat_id, "detect")
        return await send_message(
            chat_id,
            "Напишите свой вопрос, и ИИ сам поймёт, чем помочь 🤖",
        )

    # --- /start ---
    if text.lower() == "/start":
        if not is_confirmed(chat_id):
            return await send_message(chat_id, **request_age_confirmation(chat_id))
        await register_loyalty_card(chat_id)
        return await send_message(
            chat_id,
            get_translated_text(chat_id, "menu_prompt"),
            reply_markup=get_main_menu(chat_id)
        )

    # --- Каталог ---
    if text.lower() in ["каталог", "🛍 каталог", "catalog", "🛍 catalog", "catálogo", "🛍 catálogo"]:
        return await handle_catalog_overview(chat_id, send_message)

    # --- Элитный алкоголь ---
    if text.lower() in ["🌟 элитный алкоголь", "👑 элитный алкоголь", "элитный алкоголь", "премиум",
                        "elite alcohol", "👑 elite alcohol",
                        "alcohol premium", "👑 alcohol premium"]:
        return await handle_elite(chat_id, send_message)

    # --- Информация о компании ---
    if text.strip() in [
        get_translated_text(chat_id, "btn_info"),
        "ℹ️ Информация о компании и партнёрах",
        "ℹ️ Company Info",
        "ℹ️ Información de la empresa"
    ]:
        return await handle_info(chat_id, send_message)

    # --- Язык ---
    if text.strip() in [
        get_translated_text(chat_id, "btn_language"),
        "🌐 Выбрать язык", "Выбрать язык", "язык",
        "🌐 Choose Language", "Choose Language",
        "🌐 Elegir idioma", "Elegir idioma"
    ]:
        return await handle_language_selection(chat_id, send_message)

    # --- Карта лояльности ---
    if text.strip() in [
        get_translated_text(chat_id, "btn_loyalty"),
        "🎁 Карта лояльности", "карта лояльности",
        "🎁 Loyalty Card", "loyalty card",
        "🎁 Tarjeta de fidelidad", "tarjeta de fidelidad"
    ]:
        status, data = await run_in_threadpool(register_loyalty_card, chat_id)
        if status == "created":
            return await send_message(chat_id, "🎉 Ваша карта лояльности успешно создана!")
        elif status == "exists":
            tier = data.get("tier", "Bronze").capitalize()
            total_orders = data.get("total_orders", 0)
            return await send_message(chat_id,
                f"🎁 *Ваша карта лояльности уже активна!*\n\n"
                f"• Уровень: `{tier}`\n"
                f"• Заказов: `{total_orders}`\n\n"
                f"Накопите больше — получите бонусы! 💾"
            )
        else:
            return await send_message(chat_id, "⚠️ Не удалось проверить карту. Попробуйте позже.")

    # --- Баланс / Статистика ---
    if text.lower() in ["/баланс", "/статистика", "баланс", "статистика"]:
        status, data = await run_in_threadpool(register_loyalty_card, chat_id)
        if status == "exists":
            total = float(data.get("total_amount", 0) or 0)
            if total >= 1_000_000:
                tier = "Gold"
                bonus_info = "Скидка 10% и приоритетная поддержка 👑"
            elif total >= 100_000:
                tier = "Silver"
                bonus_info = "Скидка 5% на все покупки 🎉"
            else:
                tier = "Bronze"
                bonus_info = "1% бонус за каждую покупку 😊"

            return await send_message(chat_id,
                f"📊 *Ваша карта лояльности:*\n\n"
                f"• Уровень: `{tier}`\n"
                f"• Сумма покупок: `{int(total):,}₽`\n"
                f"• Бонусы: {bonus_info}\n\n"
                f"Продолжайте заказывать — и получите больше! 💼"
            )
        else:
            return await send_message(chat_id, "⚠️ Не удалось получить данные карты.")

    return await send_message(
        chat_id,
        text=get_translated_text(chat_id, "menu_prompt"),
        reply_markup=get_main_menu(chat_id)
    )
