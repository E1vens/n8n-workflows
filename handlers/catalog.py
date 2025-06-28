from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from fastapi.concurrency import run_in_threadpool
from utils.supabase import get_distinct_categories
from urllib.parse import quote

async def handle_catalog_overview(chat_id: int, send_message):
    categories = await run_in_threadpool(get_distinct_categories)
    if not categories:
        return await send_message(chat_id, "⚠️ Категории не найдены.")

    # 👇 Каждая категория — отдельная кнопка
    keyboard = [
        [InlineKeyboardButton(text=cat, callback_data=f"category|{quote(cat)}|1")]
        for cat in categories
    ]
    markup = InlineKeyboardMarkup(keyboard).to_dict()

    return await send_message(chat_id, "📦 Выберите категорию:", reply_markup=markup)
