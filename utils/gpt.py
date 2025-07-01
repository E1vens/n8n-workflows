import os
from openai import AsyncOpenAI
from typing import List, Dict

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def ask_gpt(messages: List[Dict], model: str = "gpt-3.5-turbo") -> str:
    response = await client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content
