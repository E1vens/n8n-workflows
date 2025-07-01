from fastapi import FastAPI, Request
from handlers.catalog import handle_catalog_overview, handle_category_selection
from handlers.buttons import get_main_menu
from handlers.age import is_confirmed, request_age_confirmation, handle_age_confirmation
from handlers.info import handle_info
from handlers.elite import handle_elite
from handlers.language import handle_language_selection, set_user_language, get_translated_text
from handlers.loyalty import register_loyalty_card
from fastapi.concurrency import run_in_threadpool
from config import TELEGRAM_API_URL
from utils.supabase import set_ai_mode, get_ai_mode, clear_ai_mode
from utils.gpt import ask_gpt
import httpx
import json
import traceback

app = FastAPI()

# Отправка сообщений в Telegram
async def send_message(chat_id: int, text: str, reply_markup: dict | None = None, photo: str | None = None):
    payload = {"chat_id": chat_id}

    if photo:
        payload.update({"photo": photo, "caption": text})
        method = "sendPhoto"
    else:
        payload["text"] = text
        if reply_markup:
            payload["reply_markup"] = reply_markup
        method = "sendMessage"

    print("\ud83d\udce4 Payload:", json.dumps(payload, indent=2, ensure_ascii=False))

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{TELEGRAM_API_URL}/{method}", json=payload)
        print("\ud83d\udce5 Ответ Telegram:", response.status_code, response.content.decode())

# --- Генерация кнопок выбора режима ---
def get_ai_mode_keyboard():
    return {
        "inline_keyboard": [[
            {"text": "🔍 Поиск товаров", "callback_data": "ai:mode:search"}
        ], [
            {"text": "💬 Живой чат", "callback_data": "ai:mode:chat"}
        ], [
            {"text": "❓ Вопрос про компанию", "callback_data": "ai:mode:faq"}
        ]]
    }

# --- Кнопка завершения ИИ-сессии ---
def get_ai_stop_keyboard():
    return {
        "inline_keyboard": [[
            {"text": "❌ Завершить диалог", "callback_data": "ai:stop"}
        ]]
    }

@app.post("/webhook")
async def telegram_webhook(req: Request):
    print("\ud83d\udce5 Получен запрос от Telegram")

    try:
        data = await req.json()
        print("\ud83d\udce6 Данные от Telegram:", json.dumps(data, indent=2, ensure_ascii=False))

        chat_id = None
        text = ""

        # Сообщение от пользователя
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text")

            if not text:
                print("\ud83d\udcff Пустое сообщение — игнорируем")
                return {"ok": True}

            text = text.strip()
            print(f"\ud83d\udce9 Сообщение от пользователя: {text}")

            # --- СНАЧАЛА проверяем возраст ---
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

            # --- GPT-режим: обрабатываем сообщения в активном режиме ---
            ai_mode = get_ai_mode(chat_id)
            if ai_mode:
                messages = [
                    {"role": "system", "content": "Ты — ИИ-ассистент по алкоголю. Отвечай по теме, вежливо."},
                    {"role": "user", "content": text}
                ]
                reply = await ask_gpt(messages)
                return await send_message(chat_id, reply, reply_markup=get_ai_stop_keyboard())

            # --- Обработка команды /start ---
            if text.lower() == "/start":
                await register_loyalty_card(chat_id)
                return await send_message(
                    chat_id,
                    get_translated_text(chat_id, "menu_prompt"),
                    reply_markup=get_main_menu(chat_id)
                )

            # --- Команда Каталог ---
            if text.lower() in [
                "каталог", "\ud83c\udfcd каталог",
                "catalog", "\ud83c\udfcd catalog",
                "cat\u00e1logo", "\ud83c\udfcd cat\u00e1logo"
            ]:
                return await handle_catalog_overview(chat_id, send_message)

            # --- Элитный алкоголь ---
            if text.lower() in [
                "\ud83c\udf1f элитный алкоголь", "\ud83d\udc51 элитный алкоголь", "элитный алкоголь", "премиум",
                "elite alcohol", "\ud83d\udc51 elite alcohol",
                "alcohol premium", "\ud83d\udc51 alcohol premium"
            ]:
                return await handle_elite(chat_id, send_message)

            # --- ИИ консультант ---
            if text.lower() in [
                "\ud83e\udde0 ии консультант", "ии консультант",
                "ai assistant", "asistente ia"
            ]:
                return await send_message(chat_id, "Выберите режим работы ИИ:", reply_markup=get_ai_mode_keyboard())

            # --- Информация о компании ---
            if text.strip() in [
                get_translated_text(chat_id, "btn_info"),
                "\u2139\ufe0f Информация о компании и парт\u00ebрах",
                "\u2139\ufe0f Company Info",
                "\u2139\ufe0f Informaci\u00f3n de la empresa"
            ]:
                return await handle_info(chat_id, send_message)

            # --- Выбор языка ---
            if text.strip() in [
                get_translated_text(chat_id, "btn_language"),
                "\ud83c\udf10 Выбрать язык", "Выбрать язык", "язык",
                "\ud83c\udf10 Choose Language", "Choose Language",
                "\ud83c\udf10 Elegir idioma", "Elegir idioma"
            ]:
                return await handle_language_selection(chat_id, send_message)

            # --- По умолчанию ---
            return await send_message(
                chat_id,
                text=get_translated_text(chat_id, "menu_prompt"),
                reply_markup=get_main_menu(chat_id)
            )

        # --- Callback Query ---
        elif "callback_query" in data:
            callback = data["callback_query"]
            chat_id = callback["from"]["id"]
            data_value = callback.get("data", "").strip()
            print(f"\ud83d\udccf Callback получен: {data_value}")

            if data_value.startswith("age:"):
                result = handle_age_confirmation(chat_id, data_value)
                return await send_message(
                    chat_id,
                    text=result["text"],
                    reply_markup=result.get("reply_markup")
                )

            if data_value.startswith("lang:"):
                lang_code = data_value.split(":")[1]
                set_user_language(chat_id, lang_code)
                return await send_message(
                    chat_id,
                    text=get_translated_text(chat_id, "language_set"),
                    reply_markup=get_main_menu(chat_id)
                )

            if data_value.startswith("cat|"):
                try:
                    parts = data_value.split("|")
                    cat_id = parts[1]
                    page = int(parts[2])
                    sort = parts[3] if len(parts) > 3 else "asc"
                    return await handle_category_selection(chat_id, cat_id, send_message, page, sort)
                except Exception as e:
                    print("\u274c Ошибка разбора callback 'cat|...':", e)
                    return await send_message(chat_id, "\u26a0\ufe0f Не удалось загрузить товары.")

            if data_value.startswith("ai:mode:"):
                mode = data_value.split(":")[2]
                set_ai_mode(chat_id, mode)
                return await send_message(
                    chat_id,
                    f"✅ Режим ИИ `{mode}` активирован. Напишите свой вопрос:",
                    reply_markup=get_ai_stop_keyboard()
                )

            if data_value == "ai:stop":
                clear_ai_mode(chat_id)
                return await send_message(
                    chat_id,
                    "\ud83d\udd15 Диалог с ИИ завершён.",
                    reply_markup=get_main_menu(chat_id)
                )

        return {"ok": True}

    except Exception as e:
        print("\u274c ГЛОБАЛЬНАЯ ОШИБКА:", str(e))
        traceback.print_exc()
        return {"ok": True}
