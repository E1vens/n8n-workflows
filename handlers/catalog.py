# handlers/catalog.py

import re
from utils.supabase import match_documents_by_category
from fastapi.concurrency import run_in_threadpool


async def handle_category_selection(chat_id: int, text: str, send_message):
    match = re.match(r"category:(?P<cat>[^&]+)(?:&page=(?P<page>\d+))?", text)
    if not match:
        return await send_message(chat_id, "⚠️ Неверный формат категории.")

    category = match.group("cat")
    page = int(match.group("page") or 1)

    results = await run_in_threadpool(match_documents_by_category, category, "asc", page, 10)
    if not results:
        return await send_message(chat_id, f"В категории *{category}* ничего не найдено.")

    reply = "\n\n".join([
        f"*{item.get('title', 'Без названия')}*\n"
        f"Цена: {item.get('price', '?')}\u20bd • "
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
