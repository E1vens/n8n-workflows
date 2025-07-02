from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from handlers.catalog import handle_catalog_overview, handle_category_selection
from handlers.buttons import get_main_menu
from handlers.age import is_confirmed, request_age_confirmation, handle_age_confirmation
from handlers.info import handle_info
from handlers.elite import handle_elite
from handlers.language import handle_language_selection, set_user_language, get_translated_text
from handlers.loyalty import register_loyalty_card
from handlers.ai import set_ai_mode, get_ai_mode, clear_ai_mode, ask_gpt, handle_text_message_ai
from config import TELEGRAM_API_URL
import httpx
import json
import traceback

app = FastAPI()

# --- Кнопки выбора режима ИИ ---
def get_ai_mode_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "🔍 Поиск товаров", "callback_data": "ai:mode:search"}],
            [{"text": "💬 Живой чат", "callback_data": "ai:mode:chat"}],
            [{"text": "❓ Вопрос про компанию", "callback_data": "ai:mode:faq"}]
        ]
    }

def get_ai_stop_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "❌ Завершить диалог", "callback_data": "ai:stop"}]
        ]
    }

# --- Отправка сообщений в Telegram ---
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

    print("📤 Payload:", json.dumps(payload, indent=2, ensure_ascii=False))

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{TELEGRAM_API_URL}/{method}", json=payload)
        print("📥 Ответ Telegram:", response.status_code, response.content.decode())

@app.post("/webhook")
async def telegram_webhook(req: Request):
    print("📥 Получен запрос от Telegram")

    try:
        data = await req.json()
        print("📦 Данные от Telegram:", json.dumps(data, indent=2, ensure_ascii=False))

        chat_id = None
        text = ""

        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text")

            if not text:
                print("📟 Пустое сообщение — игнорируем")
                return {"ok": True}

            text = text.strip()
            print(f"📩 Сообщение от пользователя: {text}")

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

            # --- /stop ---
            if text.lower() == "/stop":
                clear_ai_mode(chat_id)
                return await send_message(chat_id, "🛑 ИИ-режим завершён.", reply_markup=get_main_menu(chat_id))

            # --- Если ИИ активен — пробуем обработать GPT ---
            ai_mode = get_ai_mode(chat_id)


            reply = await handle_text_message_ai(chat_id, text)
            if reply:
                return await send_message(chat_id, reply)

            return await send_message(
                chat_id,
                "🤖 Я пока не понял, как вам помочь. Попробуйте переформулировать вопрос или выберите режим заново."
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

            # --- ИИ консультант ---
            if text.lower() in ["🤖 ии консультант", "ии консультант", "ai assistant", "asistente ia"]:
                 return await send_message(chat_id, "Напишите свой вопрос, и ИИ сам поймёт, чем помочь 🤖")

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
                    total = data.get("total_amount", 0) or 0
                    total = float(total)
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

            # --- По умолчанию ---
            if get_ai_mode(chat_id):
                return await send_message(
                    chat_id,
                    "⚠️ Чтобы использовать эту функцию, сначала завершите диалог с ИИ.\n\nНапишите `/stop`."
                )

            return await send_message(
                chat_id,
                text=get_translated_text(chat_id, "menu_prompt"),
                reply_markup=get_main_menu(chat_id)
            )


        elif "callback_query" in data:
            callback = data["callback_query"]
            chat_id = callback["from"]["id"]
            data_value = callback.get("data", "").strip()
            print(f"🔢 Callback получен: {data_value}")

            # --- 1. Подтверждение возраста — всегда разрешено
            if data_value.startswith("age:"):
                result = handle_age_confirmation(chat_id, data_value)
                clear_ai_mode(chat_id)
                return await send_message(
                    chat_id,
                    text=result["text"],
                    reply_markup=result.get("reply_markup")
                )

            # --- 2. Если ИИ-режим активен, блокируем все, кроме ai: (иначе невозможно будет выйти из ИИ)
            if get_ai_mode(chat_id) and not data_value.startswith("ai:"):
                return await send_message(
                    chat_id,
                    "⚠️ Чтобы использовать эту функцию, сначала завершите диалог с ИИ.\n\nНапишите `/stop`."
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

            # --- 7. По умолчанию — главное меню
            return await send_message(
                chat_id,
                text=get_translated_text(chat_id, "menu_prompt"),
                reply_markup=get_main_menu(chat_id)
            )

        return {"ok": True}


    except Exception as e:
        print("❌ ГЛОБАЛЬНАЯ ОШИБКА:", str(e))
        traceback.print_exc()
        return {"ok": True}
