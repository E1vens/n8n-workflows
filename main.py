from fastapi import FastAPI, Request
from handlers.catalog import handle_catalog_overview, handle_category_selection
from handlers.buttons import get_main_menu
from handlers.age import is_confirmed, request_age_confirmation, handle_age_confirmation
from handlers.info import handle_info
from handlers.elite import handle_elite
from handlers.language import handle_language_selection, set_user_language, get_translated_text
from config import TELEGRAM_API_URL
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

        # Сообщение от пользователя
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text")

            if not text:
                print("📭 Пустое сообщение — игнорируем")
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

            # --- Обработка команды /start ---
            if text.lower() == "/start":
                if not is_confirmed(chat_id):
                    return await send_message(chat_id, **request_age_confirmation(chat_id))

                return await send_message(
                    chat_id,
                    get_translated_text(chat_id, "menu_prompt"),
                    reply_markup=get_main_menu(chat_id)
                )

            # --- Команда Каталог (после подтверждения возраста) ---
            if text.lower() in [
                "каталог", "🛍 каталог",
                "catalog", "🛍 catalog",
                "catálogo", "🛍 catálogo"
            ]:
                return await handle_catalog_overview(chat_id, send_message)

            if text.lower() in [
                "🌟 элитный алкоголь", "👑 элитный алкоголь", "элитный алкоголь", "премиум",
                "elite alcohol", "👑 elite alcohol",
                "alcohol premium", "👑 alcohol premium"
            ]:
                return await handle_elite(chat_id, send_message)

            if text.lower() in [
                "🤖 ии консультант", "ии консультант",
                "ai assistant", "asistente ia"
            ]:
                return await send_message(chat_id, "ИИ ассистент пока не реализован.")

            if text.strip() in [
                get_translated_text(chat_id, "btn_info"),
                "ℹ️ Информация о компании и партнёрах",
                "ℹ️ Company Info",
                "ℹ️ Información de la empresa"
            ]:
                return await handle_info(chat_id, send_message)

            if text.strip() in [
                get_translated_text(chat_id, "btn_language"),
                "🌐 Выбрать язык", "Выбрать язык", "язык",
                "🌐 Choose Language", "Choose Language",
                "🌐 Elegir idioma", "Elegir idioma"
            ]:
                return await handle_language_selection(chat_id, send_message)

            return await send_message(
                chat_id,
                text=get_translated_text(chat_id, "menu_prompt"),
                reply_markup=get_main_menu(chat_id)
            )

        elif "callback_query" in data:
            callback = data["callback_query"]
            chat_id = callback["from"]["id"]
            data_value = callback.get("data", "").strip()
            print(f"📲 Callback получен: {data_value}")

            if data_value.startswith("age:"):
                result = handle_age_confirmation(chat_id, data_value)
                return await send_message(chat_id, result["text"], reply_markup=result.get("reply_markup"))

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
                    _, cat_id, page = data_value.split("|")
                    return await handle_category_selection(chat_id, cat_id, send_message, int(page))
                except Exception as e:
                    print("❌ Ошибка разбора callback 'cat|...':", e)
                    return await send_message(chat_id, "⚠️ Не удалось загрузить товары.")

        return {"ok": True}

    except Exception as e:
        print("❌ ГЛОБАЛЬНАЯ ОШИБКА:", str(e))
        traceback.print_exc()
        return {"ok": True}
