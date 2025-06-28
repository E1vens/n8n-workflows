from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from math import ceil
from fastapi.concurrency import run_in_threadpool
from utils.supabase import get_top_products_by_category, get_distinct_categories
from urllib.parse import quote

PAGE_SIZE = 5  # количество товаров на странице

# ✅ Показывает список категорий (каталог)
async def handle_catalog_overview(chat_id: int, send_message):
    categories = await run_in_threadpool(get_distinct_categories)
    if not categories:
        return await send_message(chat_id, "⚠️ Категории не найдены.")

    buttons = [
        [InlineKeyboardButton(cat, callback_data=f"category|{quote(cat)}|1")]
        for cat in categories
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    return await send_message(chat_id, "Выберите категорию:", reply_markup=reply_markup)

# ✅ Показывает товары выбранной категории постранично
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
        await send_message(chat_id, text, reply_markup=None, photo=product.get('image_url'))

    # 🔘 Кнопки навигации между страницами
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Предыдущая", callback_data=f"category|{quote(category)}|{page - 1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("➡️ Следующая", callback_data=f"category|{quote(category)}|{page + 1}"))

    if nav_buttons:
        reply_markup = InlineKeyboardMarkup([nav_buttons])
        return await send_message(chat_id, f"Страница {page}/{total_pages}", reply_markup=reply_markup)
    else:
        return await send_message(chat_id, f"Страница {page}/{total_pages}")
