from fastapi import FastAPI, Request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import httpx

app = FastAPI()

# 🔒 Подтверждение возраста
confirmed_users = set()

# ✅ Главное меню (reply-кнопки)
def get_main_menu():
    keyboard = [
        [KeyboardButton("🛍 Каталог"), KeyboardButton("🤖 ИИ консультант")],
        [KeyboardButton("ℹ️ Информация о товаре"), KeyboardButton("🌐 Выбрать язык")],
        [KeyboardButton("🎁 Карта лояльности")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ✅ Возрастные кнопки
def get_age_buttons():
    keyboard = [
        [
            InlineKeyboardButton("Да, мне есть 18", callback_data="age:yes"),
            InlineKeyboardButton("Нет", callback_data="age:no")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ✅ Категории
def get_category_buttons():
    keyboard = [
        [InlineKeyboardButton("Виски", callback_data="category:Виски")],
        [InlineKeyboardButton("Вино", callback_data="category:Вино")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ✅ Отправка сообщения
async def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup.to_dict()

    async with httpx.AsyncClient() as client:
        await client.post("https://api.telegram.org/bot7717544481:AAGQhV8QF2h-cHJIsUs9pZOp12nKEHA16eU/sendMessage", json=payload)

# ✅ Обработка Telegram Webhook
@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    print("📥 ПОЛУЧЕНО:", data)

    chat_id = None
    text = ""

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip().lower()

        if text in ["/start", "старт"]:
            return await send_message(chat_id, "Подтвердите, пожалуйста, что вам есть 18 лет:", get_age_buttons())

        if chat_id not in confirmed_users:
            return await send_message(chat_id, "🚫 Доступ запрещён. Нажмите /start и подтвердите возраст.")

        # Главное меню
        if text == "🛍 каталог":
            return await send_message(chat_id, "Выберите категорию:", get_category_buttons())

        if text == "🤖 ии консультант":
            return await send_message(chat_id, "ИИ-консультант скоро будет доступен", get_main_menu())

        if text == "🔙 выйти из ии":
            return await send_message(chat_id, "ИИ отключён.", get_main_menu())

        if text == "ℹ️ информация о товаре":
            return await send_message(chat_id, "Напишите название товара")

        if text == "🌐 выбрать язык":
            return await send_message(chat_id, "Пока доступен только русский язык")

        if text == "🎁 карта лояльности":
            return await send_message(chat_id, "🔖 Карта доступна в магазине при покупке")

        return await send_message(chat_id, "Выберите действие в меню", get_main_menu())

    elif "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["from"]["id"]
        text = callback["data"]
        callback_id = callback["id"]

        # Подтверждаем callback
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot7717544481:AAGQhV8QF2h-cHJIsUs9pZOp12nKEHA16eU/answerCallbackQuery",
                json={"callback_query_id": callback_id}
            )

        if text == "age:yes":
            confirmed_users.add(chat_id)
            return await send_message(chat_id, "✅ Спасибо! Вот доступные категории:", get_category_buttons())

        elif text == "age:no":
            return await send_message(chat_id, "🚫 Доступ запрещён.")

        elif text.startswith("category:"):
            category = text.split(":")[1]
            return await send_message(chat_id, f"Вы выбрали категорию: {category}")

    return {"ok": True}
