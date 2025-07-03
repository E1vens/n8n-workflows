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
                "Ты ассистент, который должен классифицировать входящие сообщения пользователей по их намерениям.\n"
                "Ты должен выбрать одну из трёх чётких категорий:\n\n"
                "1. `search` — если пользователь ищет товар, упоминает алкоголь, цену, объём, крепость, скидки, категории "
                "(например: 'водка до 1000', 'покажи вино', 'что есть из текилы', "
                "'список товаров', 'покажи товары из базы', 'list of products').\n"
                "2. `company` — если пользователь интересуется информацией о компании: доставка, возврат, контакты, сотрудничество, "
                "лицензия, регионы поставок, история, реквизиты.\n"
                "3. `chat` — если пользователь здоровается, прощается, шутит, говорит 'привет', 'пока', просит помощи, ведёт "
                "обычный диалог без уточнений.\n\n"
                "Отвечай только одним словом: `search`, `company`, или `chat`. Никаких пояснений."
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
