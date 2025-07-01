import os
import openai
from typing import List, Dict


openai.api_key = os.getenv("OPENAI_API_KEY")

async def ask_gpt(messages: List[Dict], model="gpt-3.5-turbo") -> str:
    response = openai.ChatCompletion.acreate(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content
