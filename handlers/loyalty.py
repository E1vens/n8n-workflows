import requests
from config import SUPABASE_URL, SUPABASE_KEY
from datetime import datetime
from fastapi import Request
import httpx

# Функция регистрации или проверки карты в Supabase через REST API
def register_loyalty_card(chat_id: int) -> tuple[str, dict | None]:
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    check_url = f"{SUPABASE_URL}/rest/v1/loyalty_cards?select=id,tier,total_orders&chat_id=eq.{chat_id}"

    try:
        resp = requests.get(check_url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                return "exists", data[0]  # ✅ Карта найдена — возвращаем и выходим
        else:
            print("❌ Проверка карты: ошибка", resp.status_code, resp.text)
            return "error", None
    except Exception as e:
        print("❌ Ошибка при проверке карты:", e)
        return "error", None

    # ⛳ Если карта не найдена — создаём
    insert_url = f"{SUPABASE_URL}/rest/v1/loyalty_cards"
    payload = [{
        "chat_id": str(chat_id),
        "tier": "bronze",
        "total_orders": 0,
        "birthday": None,
        "created_at": datetime.utcnow().isoformat()
    }]

    try:
        resp = requests.post(insert_url, headers=headers, json=payload)
        resp.raise_for_status()
        return "created", None
    except Exception as e:
        print("❌ Ошибка регистрации карты:", e)
        return "error", None


# Асинхронная функция отправки сообщений через Telegram API
async def send_message(chat_id: int, text: str, reply_markup: dict | None = None):
    from config import TELEGRAM_API_URL
    async with httpx.AsyncClient() as client:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        await client.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

# Отправка информации о карте лояльности
async def send_loyalty_info(chat_id: int):
    text = (
        "🎁 *Карта лояльности Veld21*\n\n"
        "Наша карта лояльности — это ваш персональный бонусный счёт, который позволяет получать приятные подарки и скидки за покупки в нашем магазине.\n\n"
        "📌 *Как это работает:*\n"
        "• За каждый заказ вы получаете баллы (очки).\n"
        "• Накопленные баллы повышают ваш уровень (Bronze, Silver, Gold и т.д.).\n"
        "• Чем выше уровень — тем больше бонусов и эксклюзивных предложений.\n"
        "• Вы можете отслеживать количество заказов и статус карты в любое время через бота.\n\n"
        "💡 *Почему это выгодно:*\n"
        "✅ Эксклюзивные скидки и акции только для держателей карты.\n"
        "✅ Быстрое начисление и списание баллов.\n"
        "✅ Персональные предложения и подарки.\n\n"
        "Чтобы начать пользоваться, просто сделайте первый заказ, а бот автоматически создаст вашу карту и будет следить за вашими бонусами!\n\n"
        "Если есть вопросы — пишите, мы всегда рады помочь! 😊"
    )
    await send_message(chat_id, text)

# Основная функция-обработчик команды "Карта лояльности"
async def handle_loyalty_card(chat_id: int):
    status, data = await run_in_threadpool(register_loyalty_card, chat_id)
    if status == "exists" and data:
        tier = data.get("tier", "Bronze").capitalize()
        total_orders = data.get("total_orders", 0)
        text = (
            f"🎁 *Ваша карта лояльности уже активна!*\n\n"
            f"• Уровень: `{tier}`\n"
            f"• Заказов: `{total_orders}`\n\n"
            f"Накопите больше — получите бонусы! 💎"
        )
        await send_message(chat_id, text)
    elif status == "created":
        await send_message(chat_id, "🎉 Ваша карта лояльности успешно создана!")
    else:
        await send_message(chat_id, "⚠️ Не удалось проверить карту. Попробуйте позже.")

# Чтобы использовать run_in_threadpool (FastAPI util)
from fastapi.concurrency import run_in_threadpool
