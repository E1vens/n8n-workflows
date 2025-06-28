from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from fastapi.concurrency import run_in_threadpool
from utils.supabase import get_top_products_by_category, get_distinct_categories
from math import ceil
from urllib.parse import quote

PAGE_SIZE = 5

async def handle_catalog_overview(chat_id: int, send_message):
    categories = await run_in_threadpool(get_distinct_categories)
    if not categories:
        return await send_message(chat_id, "⚠️ Категории не найдены.")

    keyboard = [
        [InlineKeyboardButton(text=title, callback_data=f"category|{quote(title)}|1")]
        for title in categories
    ]
    return await send_message(chat_id, "Выберите категорию товара:", InlineKeyboardMarkup(keyboard).to_dict())

async def handle_category_selection(chat_id: int, category: str, send_message, page: int = 1):
    all_products = await run_in_threadpool(get_top_products_by_category, category)
    if not all_products:
        return await send_message(chat_id, f"⚠️ В категории '{category}' ничего не найдено.")

    total_pages = ceil(len(all_products) / PAGE_SIZE)
    page = max(1, min(page, total_pages))
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    products = all_products[start:end]

    for product in products:
        text = (
            f"*{product.get('title', 'Без названия')}*\n"
            f"Цена: {product.get('price', '?')}₽\n"
            f"Объём: {product.get('volume', '?')} • "
            f"Крепость: {product.get('strength', '?')}\n"
            f"[🔗 Ссылка на товар]({product.get('product_url', '#')})"
        )
        await send_message(chat_id, text, photo=product.get("image_url"))

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"category|{quote(category)}|{page - 1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("➡️ Далее", callback_data=f"category|{quote(category)}|{page + 1}"))

    if nav_buttons:
        markup = InlineKeyboardMarkup([nav_buttons]).to_dict()
        await send_message(chat_id, f"Страница {page}/{total_pages}", reply_markup=markup)
    else:
        await send_message(chat_id, f"Страница {page}/{total_pages}")
