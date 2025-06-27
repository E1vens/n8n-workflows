from fastapi import FastAPI, Request
from telegram import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from config import TELEGRAM_API_URL
from utils.embeddings import get_embedding
from utils.supabase import match_documents
import httpx

app = FastAPI()

# ✅ Проверка подтверждения возраста
confirmed_users = set()

def is_confirmed(chat_id):
    return chat_id in confirmed_users

def handle_age_confirmation(chat_id, data):
    print(f"👤 ОБРАБОТКА возраста: chat_id={chat_id}, data={data}")
    if data == "age:yes":
        confirmed_users.add(chat_id)
        return {
            "text": "✅ Спасибо! Вот доступные категории:",
            "reply_markup": get_category_buttons()
        }
    else:
        return {
            "text": "🚫 Доступ запрещён. Вы не подтвердили возраст."
        }

def request_age_confirmation():
    keyboard = [
        [
            InlineKeyboardButton("Да, мне есть 18", callback_data="age:yes"),
            InlineKeyboardButton("Нет", callback_data="age:no")
        ]
    ]
    return {
        "text": "Подтвердите, пожалуйста, что вам есть 18 лет:",
        "reply_markup": InlineKeyboardMarkup(keyboard)
    }

def get_category_buttons():
    categories = [
        "Виски", "Коньяк и Арманьяк", "Кальвадос", "Водка", "Джин",
        "Шампанское и игристое", "Вино", "Крепкое вино", "Другие"
    ]
    keyboard = [[InlineKeyboardButton(text=title, callback_data=f"category:{title}")] for title in categories]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu():
    keyboard = [
        [KeyboardButton("🛍 Каталог"), KeyboardButton("🤖 ИИ консультант")],
        [KeyboardButton("ℹ️ Информация о товаре"), KeyboardButton("🌐 Выбрать язык")],
        [KeyboardButton("🎁 Карта лояльности")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_ai_exit_button():
    keyboard = [[KeyboardButton("🔙 Выйти из ИИ")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

ai_enabled = set()

def is_ai_active(chat_id):
    return chat_id in ai_enabled

def activate_ai(chat_id):
    ai_enabled.add(chat_id)

def deactivate_ai(chat_id):
    ai_enabled.discard(chat_id)

async def send_message(chat_id: int, text: str, reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup.to_dict()

    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    print("📥 ПОЛУЧЕНО:", data)

    chat_id = None
    text = ""

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()

    elif "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["from"]["id"]
        text = callback.get("data", "").strip()
        callback_id = callback["id"]

        print(f"✅ НАЖАТА inline-кнопка: {text}")

        async with httpx.AsyncClient() as client:
            await client.post(
                f"{TELEGRAM_API_URL}/answerCallbackQuery",
                json={"callback_query_id": callback_id}
            )

        if text.startswith("age:"):
            print(f"🧪 ВРЕМЕННЫЙ ответ на age-кнопку: {text}")
            return await send_message(chat_id, "✅ Спасибо за подтверждение возраста.")
            

        if text.startswith("category:"):
            return await send_message(chat_id, f"Вы выбрали категорию: {text.split(':', 1)[1]}")

        return {"ok": True}

    if not chat_id or not text:
        return {"ok": True}

    if text.lower() in ["/start", "старт"]:
        return await send_message(chat_id, "✅ Добро пожаловать! Вот доступные категории:", get_category_buttons())

    #if not is_confirmed(chat_id):
     #   return await send_message(chat_id, "🚫 Доступ запрещён. Нажмите /start и подтвердите возраст.")

    if text == "🛍 Каталог":
        return await send_message(chat_id, "Выберите категорию:", get_category_buttons())

    if text.startswith("category:"):
        return await send_message(chat_id, f"Вы выбрали категорию: {text.split(':', 1)[1]}")

    if text == "🤖 ИИ консультант":
        activate_ai(chat_id)
        return await send_message(chat_id, "ИИ-консультант активирован. Задай свой вопрос:", get_ai_exit_button())

    if text == "🔙 Выйти из ИИ":
        deactivate_ai(chat_id)
        return await send_message(chat_id, "ИИ-консультант отключён. Выберите действие из меню:", get_main_menu())

    if text == "ℹ️ Информация о товаре":
        return await send_message(chat_id, "Отправьте название товара — я найду описание и характеристики.")

    if text == "🌐 Выбрать язык":
        return await send_message(chat_id, "Язык пока только русский. Скоро добавим другие!")

    if text == "🎁 Карта лояльности":
        return await send_message(chat_id, "🔖 Карта лояльности доступна в магазине. Оформим при покупке.")

    if is_ai_active(chat_id):
        embed = await get_embedding(text)
        results = await match_documents(embed)

        if not results:
            return await send_message(chat_id, "Ничего не найдено. Попробуй переформулировать запрос.")

        reply = "\n\n".join([
            f"*{item['metadata'].get('title', 'Без названия')}*\n"
            f"Цена: {item['metadata'].get('price', '?')}₽ • "
            f"Объём: {item['metadata'].get('volume', '?')} • "
            f"Крепость: {item['metadata'].get('strength', '?')}\n"
            f"🔗 [Ссылка на товар]({item['metadata'].get('product_url', '#')})"
            for item in results[:10]
        ])
        return await send_message(chat_id, reply)

    return {"ok": True}
