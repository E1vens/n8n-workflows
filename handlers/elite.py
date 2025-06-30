from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from handlers.language import auto_translate_if_needed

elite_ru = """🌟 *Элитный алкоголь от ВЕЛЬД-21*

Мы поставляем уникальные и редкие напитки со всего мира. Наши эксперты лично посещают лучшие винокурни Европы, Азии и Америки, подписывают эксклюзивные контракты и обеспечивают полную легализацию продукции в России.

Вы можете быть уверены:
✅ 100% оригинальный алкоголь
✅ Только официальные поставки
✅ Доступ к редким коллекционным позициям
✅ Персональный подбор и сопровождение

Для клиентов доступны индивидуальные условия и приватные коллекции."""

async def handle_elite(chat_id: int, send_message):
    text = await auto_translate_if_needed(chat_id, elite_ru)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 Получить консультацию", url="https://veld21.ru/contact/"),
            InlineKeyboardButton("🔒 Премиальный каталог", url="https://veld21.ru/katalog/")
        ]
    ])

    await send_message(chat_id, text, reply_markup=keyboard.to_dict())
