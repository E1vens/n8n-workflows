from fastapi import FastAPI, Request
import httpx

app = FastAPI()

TELEGRAM_TOKEN = "7717544481:AAGQhV8QF2h-cHJIsUs9pZOp12nKEHA16eU"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    print("📥 Получено:", data)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        if data["message"].get("text") == "/start":
            keyboard = {
                "inline_keyboard": [[
                    {"text": "Нажми меня", "callback_data": "test"}
                ]]
            }
            await send_message(chat_id, "Привет! Тестовая кнопка ниже:", keyboard)

    elif "callback_query" in data:
        chat_id = data["callback_query"]["from"]["id"]
        data_text = data["callback_query"]["data"]
        await answer_callback(data["callback_query"]["id"])
        await send_message(chat_id, f"Вы нажали: {data_text}")

    return {"ok": True}

async def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

async def answer_callback(callback_id):
    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API_URL}/answerCallbackQuery", json={"callback_query_id": callback_id})
