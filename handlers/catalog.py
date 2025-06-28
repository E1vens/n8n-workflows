from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from fastapi.concurrency import run_in_threadpool
from utils.supabase import get_distinct_categories, get_top_products_by_category
from math import ceil

PAGE_SIZE = 5

async def handle_catalog_overview(chat_id: int, send_message, page: int = 1):
    categories = await run_in_threadpool(get_distinct_categories)
    if not categories:
        return await send_message(chat_id, "⚠️ Категории не найдены.")

    total_pages = ceil(len(categories) / PAGE_SIZE)
    page = max(1, min(page, total_pages))
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    page_categories = categories[start:end]

    keyboard = [
        [InlineKeyboardButton(f"📦 {cat}", callback_data=f"category|{cat}|1")] for cat in page_categories
    ]

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"catalog|{page - 1}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("➡️ Далее", callback_data=f"catalog|{page + 1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    return await send_message(chat_id, "📚 Выберите категорию:", reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_category_selection(chat_id: int, category: str, send_message, page: int = 1):
    all_products = await run_in_threadpool(get_top_products_by_category, category)
    total_pages = ceil(len(all_products) / PAGE_SIZE)

    if not all_products:
        return await send_message(chat_id, f"⚠️ Товары категории '{category}' не найдены.")

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

    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Предыдущая", callback_data=f"category|{category}|{page - 1}"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton("➡️ Следующая", callback_data=f"category|{category}|{page + 1}"))
    buttons.append(InlineKeyboardButton("🔙 Назад в каталог", callback_data="catalog|1"))

    markup = InlineKeyboardMarkup([buttons])
    await send_message(chat_id, f"Страница {page}/{total_pages}", reply_markup=markup)
