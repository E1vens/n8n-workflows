from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def handle_elite(chat_id: int, send_message):
    text = (
        "🌟 *Элитный алкоголь от ВЕЛЬД-21*\n\n"
        "Мы поставляем уникальные и редкие напитки со всего мира. "
        "Наши эксперты лично посещают лучшие винокурни Европы, Азии и Америки, "
        "подписывают эксклюзивные контракты и обеспечивают полную легализацию продукции в России.\n\n"
        "Вы можете быть уверены:\n"
        "✅ 100% оригинальный алкоголь\n"
        "✅ Только официальные поставки\n"
        "✅ Доступ к редким коллекционным позициям\n"
        "✅ Персональный подбор и сопровождение\n\n"
        "Для клиентов доступны индивидуальные условия и приватные коллекции."
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 Получить консультацию", url="https://veld21.ru/contact/"),
            InlineKeyboardButton("🔒 Премиальный каталог", url="https://veld21.ru/katalog/")
        ]
    ])

    await send_message(chat_id, text, reply_markup=keyboard.to_dict())
