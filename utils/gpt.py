import os
from openai import AsyncOpenAI
from typing import List, Dict

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 💬 Ответ от GPT в режиме чата
async def ask_gpt(messages: List[Dict], model: str = "gpt-3.5-turbo") -> str:
    response = await client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content.strip()

# 🔮 Определение режима через GPT
async def detect_ai_mode_gpt(message: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "Ты классификатор входящих сообщений.\n"
                "У тебя есть три возможных категории:\n"
                "1. search — если пользователь ищет товар, интересуется ценой, фильтрацией или характеристиками.\n"
                "2. company — если пользователь спрашивает о компании, услугах, доставке, контактах, партнёрстве и т.п.\n"
                "3. chat — всё остальное: просто общение, приветствие, помощь, фразы вне тематики.\n\n"
                "Отвечай только одной категорией: `search`, `company` или `chat`."
            )
        },
        {
            "role": "user",
            "content": message
        }
    ]

    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content.strip()
