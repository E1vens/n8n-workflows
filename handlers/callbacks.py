# handlers/callbacks.py

from handlers.age import handle_age_confirmation
from handlers.language import set_user_language, get_translated_text
from handlers.buttons import get_main_menu
from handlers.ai import set_ai_mode, clear_ai_mode, get_ai_mode
from handlers.catalog import handle_category_selection

async def handle_callback_query(chat_id, data_value, send_message, get_ai_stop_keyboard):
    # --- 1. Подтверждение возраста
    if data_value.startswith("age:"):
        result = handle_age_confirmation(chat_id, data_value)
        clear_ai_mode(chat_id)
        return await send_message(
            chat_id,
            text=result["text"],
            reply_markup=result.get("reply_markup")
        )

    # --- 2. Если ИИ активен, блокируем всё кроме ai:
    if get_ai_mode(chat_id) and not data_value.startswith("ai:"):
        return await send_message(
            chat_id,
            "⚠️ Чтобы использовать эту функцию, сначала завершите диалог с ИИ.\n\nНапишите /stop."
        )

    # --- 3. Смена языка
    if data_value.startswith("lang:"):
        lang_code = data_value.split(":")[1]
        set_user_language(chat_id, lang_code)
        return await send_message(
            chat_id,
            text=get_translated_text(chat_id, "language_set"),
            reply_markup=get_main_menu(chat_id)
        )

    # --- 4. Выбор категории
    if data_value.startswith("cat|"):
        try:
            parts = data_value.split("|")
            cat_id = parts[1]
            page = int(parts[2])
            sort = parts[3] if len(parts) > 3 else "asc"
            return await handle_category_selection(chat_id, cat_id, send_message, page, sort)
        except Exception as e:
            print("❌ Ошибка разбора callback 'cat|...':", e)
            return await send_message(chat_id, "⚠️ Не удалось загрузить товары.")

    # --- 5. Смена режима ИИ
    if data_value.startswith("ai:mode:"):
        mode = data_value.split(":")[2]
        set_ai_mode(chat_id, mode)
        return await send_message(
            chat_id,
            f"✅ Режим ИИ `{mode}` активирован. Напишите ваш вопрос:",
            reply_markup=get_ai_stop_keyboard()
        )

    # --- 6. Завершить ИИ-диалог
    if data_value == "ai:stop":
        clear_ai_mode(chat_id)
        return await send_message(
            chat_id,
            "🔕 Диалог с ИИ завершён.",
            reply_markup=get_main_menu(chat_id)
        )

    # --- 7. По умолчанию
    return await send_message(
        chat_id,
        text=get_translated_text(chat_id, "menu_prompt"),
        reply_markup=get_main_menu(chat_id)
    )

