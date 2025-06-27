from fastapi import FastAPI, Request
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import httpx

app = FastAPI()

TELEGRAM_TOKEN = "8169841390:AAEqs68crr4SjcqtqNvCDVTobfxHKxBGpxQ"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

async def send_message(chat_id: int, text: str, reply_markup=None):
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

    # Сообщение от пользователя
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        if text == "/start":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Тест кнопка", callback_data="test:ok")]
            ])
            return await send_message(chat_id, "🔘 Нажми кнопку ниже:", keyboard)

    # Нажатие inline-кнопки
    elif "callback_query" in data:
        print("✅ ПОЛУЧЕН callback_query:", data["callback_query"])
        chat_id = data["callback_query"]["from"]["id"]
        return await send_message(chat_id, "✅ Нажата тестовая кнопка")

    return {"ok": True}
