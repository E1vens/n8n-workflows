from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from utils.embeddings import get_embedding
from handlers.age import handle_age_confirmation, is_confirmed, request_age_confirmation
from utils.supabase import match_documents, match_documents_by_category
from handlers.catalog import handle_catalog_overview, handle_category_selection
from handlers.buttons import get_main_menu, get_age_confirmation_buttons, get_category_buttons
from config import TELEGRAM_TOKEN, TELEGRAM_API_URL
from urllib.parse import unquote
import httpx
import re

print("✅ main.py успешно загружен")

app = FastAPI()

async def send_message(chat_id: int, text: str, reply_markup: dict | None = None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

@app.post("/webhook")
async def telegram_webhook(req: Request):
    try:
        data = await req.json()
    except Exception as e:
        print("❌ Ошибка чтения запроса:", e)
        return {"ok": False}

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

        # 👇 Поддержка кнопок с форматами category|<категория>|<страница>
        if text.startswith("category|"):
            try:
                _, raw_category, page = text.split("|")
                category = unquote(raw_category)
                return await handle_category_selection(chat_id, category, send_message, int(page))
            except Exception as e:
                print("❌ Ошибка category| обработчика:", e)
                return await send_message(chat_id, "⚠️ Ошибка обработки категории.")

        # 👇 Возврат в каталог
        if text == "🛍 Каталог":
            return await handle_catalog_overview(chat_id, send_message, 1)

    else:
        return {"ok": True}

    if not chat_id or not text:
        return await send_message(chat_id, "⚠️ Сообщение не распознано. Повторите ввод.")

    if text.startswith("age:"):
        result = handle_age_confirmation(chat_id, text)
        return await send_message(chat_id, result["text"], result.get("reply_markup"))

    if text.lower() in ["/start", "старт"]:
        return await send_message(chat_id, "Подтвердите, пожалуйста, что вам есть 18 лет:", get_age_confirmation_buttons())

    if not is_confirmed(chat_id):
        result = request_age_confirmation()
        return await send_message(chat_id, result["text"], result.get("reply_markup"))

    if text == "🛍 Каталог":
        return await send_message(chat_id, "Выберите категорию товара:", get_category_buttons())

    if text == "👑 Элитный алкоголь":
        results = await run_in_threadpool(match_documents_by_category, "Элитный", "desc", 1, 10)
        if not results:
            return await send_message(chat_id, "Элитный алкоголь не найден.")

        reply = "\n\n".join([
            f"*{item.get('title', 'Без названия')}*\n"
            f"Цена: {item.get('price', '?')}₽ • "
            f"Объём: {item.get('volume', '?')} • "
            f"Крепость: {item.get('strength', '?')}\n"
            f"🔗 [Ссылка на товар]({item.get('product_url', '#')})"
            for item in results
        ])
        return await send_message(chat_id, reply)

    if text == "🤖 ИИ консультант":
        return await send_message(chat_id, "🤖 ИИ-консультант пока в разработке. Ожидайте обновлений.")

    if text == "ℹ️ Информация о компании и партнёрах":
        return await send_message(chat_id, "Компания Veld21 работает с 2005 года. Сотрудничаем с поставщиками из Европы и СНГ.\n\n📧 info@veld21.ru\n🌐 https://veld21.ru")

    if text == "🌐 Выбрать язык":
        return await send_message(chat_id, "🌐 Пока доступен только русский язык 🇷🇺")

    if text == "🎁 Карта лояльности":
        return await send_message(chat_id, "🎁 Скоро появится карта лояльности. Следите за новостями!")

    if text.startswith("category:"):
        match = re.match(r"category:(?P<cat>[^&]+)(?:&page=(?P<page>\d+))?", text)
        if not match:
            return await send_message(chat_id, "⚠️ Неверный формат категории.")

        category = match.group("cat")
        page = int(match.group("page") or 1)

        print(f"📦 Категория: {category} | Страница: {page}")

        results = await run_in_threadpool(match_documents_by_category, category, "asc", page, 10)
        if not results:
            return await send_message(chat_id, f"В категории *{category}* ничего не найдено.")

        reply = "\n\n".join([
            f"*{item.get('title', 'Без названия')}*\n"
            f"Цена: {item.get('price', '?')}₽ • "
            f"Объём: {item.get('volume', '?')} • "
            f"Крепость: {item.get('strength', '?')}\n"
            f"🔗 [Ссылка на товар]({item.get('product_url', '#')})"
            for item in results
        ])

        next_page_btn = {
            "inline_keyboard": [[{
                "text": "➡️ Следующая страница",
                "callback_data": f"category:{category}&page={page + 1}"
            }]]
        }

        return await send_message(chat_id, reply, next_page_btn)

    embed = await get_embedding(text)
    results = await match_documents(embed)

    if not results:
        return await send_message(chat_id, "К сожалению, ничего не найдено. Попробуйте другой запрос.")

    reply = "\n\n".join([
        f"*{item['metadata'].get('title', 'Без названия')}*\n"
        f"Цена: {item['metadata'].get('price', '?')}₽ • "
        f"Объём: {item['metadata'].get('volume', '?')} • "
        f"Крепость: {item['metadata'].get('strength', '?')}\n"
        f"🔗 [Ссылка на товар]({item['metadata'].get('product_url', '#')})"
        for item in results[:10]
    ])

    if len(results) > 10:
        reply += f"\n\n_Показано 10 из {len(results)} результатов._"

    return await send_message(chat_id, reply)
