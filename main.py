@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()

    # message или callback_query
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
    elif "callback_query" in data:
        callback = data["callback_query"]
        chat_id = callback["from"]["id"]
        text = callback.get("data", "")
    else:
        return {"ok": True}

    # ✅ Обработка inline-кнопок
    if text.startswith("age:"):
        if text == "age:yes":
            confirmed_users.add(chat_id)
            return await send_message(chat_id, "✅ Спасибо! Вот доступные категории:", get_reply_markup())
        else:
            return await send_message(chat_id, "🚫 К сожалению, доступ запрещён. Повторно введите /start, если вам уже исполнилось 18.")

    # ✅ Команда /start
    if text.lower() in ["/start", "старт"]:
        return await send_message(chat_id, "Подтвердите, пожалуйста, что вам есть 18 лет:", get_age_confirmation_buttons())

    # ✅ Если возраст не подтверждён
    if chat_id not in confirmed_users:
        return await send_message(chat_id, "🚫 Доступ запрещён. Нажмите /start и подтвердите возраст.")

    # ✅ Выбор категории
    if text.startswith("category:"):
        category = text.replace("category:", "")
        results = await match_documents(category=category)
        if not results:
            return await send_message(chat_id, f"В категории *{category}* ничего не найдено.")

        reply = "\n\n".join([
            f"**{item['metadata']['title']}**\nЦена: {item['metadata']['price']}₽ • Объём: {item['metadata']['volume']} • Крепость: {item['metadata']['strength']}\n🔗 [Ссылка на товар]({item['metadata']['product_url']})"
            for item in results[:10]
        ])
        if len(results) > 10:
            reply += f"\n\n_Pоказано 10 из {len(results)} результатов._"

        return await send_message(chat_id, reply)

    # ✅ Текстовый запрос
    embed = await get_embedding(text)
    results = await match_documents(embed)

    if not results:
        return await send_message(chat_id, "К сожалению, ничего не найдено. Попробуйте другой запрос.")

    reply = "\n\n".join([
        f"**{item['metadata']['title']}**\nЦена: {item['metadata']['price']}₽ • Объём: {item['metadata']['volume']} • Крепость: {item['metadata']['strength']}\n🔗 [Ссылка на товар]({item['metadata']['product_url']})"
        for item in results[:10]
    ])
    if len(results) > 10:
        reply += f"\n\n_Pоказано 10 из {len(results)} результатов._"

    return await send_message(chat_id, reply)
