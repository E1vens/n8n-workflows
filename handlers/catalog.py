import re
import re
from fastapi.concurrency import run_in_threadpool
from utils.supabase import get_distinct_categories, get_top_products_by_category


async def handle_catalog_overview(chat_id: int, send_message):
    categories = await run_in_threadpool(get_distinct_categories)
    if not categories:
        return await send_message(chat_id, "⚠️ Категории не найдены.")

    message_parts = []

    for cat in categories:
        items = await run_in_threadpool(get_top_products_by_category, cat, 5)
        if not items:
            continue

        section = f"📦 *{cat.strip().capitalize()}*\n"
        for item in items:
            section += (
                f"• *{item.get('title', 'Без названия')}*\n"
                f"  Цена: {item.get('price', '?')}₽ • "
                f"Объём: {item.get('volume', '?')} • "
                f"Крепость: {item.get('strength', '?')}\n"
                f"  [📸 Фото]({item.get('image_url', '#')}) • [🔗 Товар]({item.get('product_url', '#')})\n\n"
            )
        message_parts.append(section)

    full_message = "\n".join(message_parts)

    # ⚠️ Ограничим длину сообщения, чтобы Telegram не выдал ошибку
    if len(full_message) > 4000:
        full_message = full_message[:3900] + "\n...\n_Каталог был обрезан из-за длины._"

    return await send_message(chat_id, full_message.strip())
