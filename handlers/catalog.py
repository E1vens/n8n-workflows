from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from fastapi.concurrency import run_in_threadpool
from utils.supabase import get_distinct_categories, get_top_products_by_category
from math import ceil

PAGE_SIZE = 5  # Показываем 5 товаров на странице

async def handle_catalog_overview(chat_id: int, send_message):
    categories = await run_in_threadpool(get_distinct_categories)
    if not categories:
        return await send_message(chat_id, "⚠️ Категории не найдены.")

    message_parts = []

    for cat in categories:
        items = await run_in_threadpool(get_top_products_by_category, cat)
        if not items:
            continue

        section = f"📦 *{cat.strip().capitalize()}*\n"
        for item in items[:5]:  # только первые 5 товаров на главной
            section += (
                f"• *{item.get('title', 'Без названия')}*\n"
                f"  Цена: {item.get('price', '?')}₽ • "
                f"Объём: {item.get('volume', '?')} • "
                f"Крепость: {item.get('strength', '?')}\n"
                f"  [📸 Фото]({item.get('image_url', '#')}) • [🔗 Товар]({item.get('product_url', '#')})\n\n"
            )
        message_parts.append(section)

    full_message = "\n".join(message_parts)

    if len(full_message) > 4000:
        full_message = full_message[:3900] + "\n...\n_Каталог был обрезан из-за длины._"

    return await send_message(chat_id, full_message.strip())


async def handle_category_selection(chat_id: int, category: str, send_message, page: int = 1):
    all_products = await run_in_threadpool(get_top_products_by_category, category)
    if not all_products:
        return await send_message(chat_id, f"⚠️ Товары категории '{category}' не найдены.")

    total_pages = ceil(len(all_products) / PAGE_SIZE)
    page = max(1, min(page, total_pages))
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    page_products = all_products[start:end]

    for product in page_products:
        text = (
            f"*{product.get('title', 'Без названия')}*\n"
            f"Цена: {product.get('price', '?')}₽\n"
            f"Объём: {product.get('volume', '?')} • "
            f"Крепость: {product.get('strength', '?')}\n"
            f"[🔗 Открыть товар]({product.get('product_url', '#')})"
        )
        await send_message(chat_id, text, photo=product.get('image_url'))

    # 🔘 Кнопки навигации
    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Предыдущая", callback_data=f"{category}|{page - 1}"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton("➡️ Следующая", callback_data=f"{category}|{page + 1}"))
    buttons.append(InlineKeyboardButton("🔙 Назад в каталог", callback_data="🛍 Каталог"))

    reply_markup = InlineKeyboardMarkup([buttons])
    await send_message(chat_id, f"Страница {page}/{total_pages}", reply_markup=reply_markup)
