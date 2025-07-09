import os
from dotenv import load_dotenv

load_dotenv()

GIT_BRANCH = os.getenv("GIT_BRANCH", "main")

if GIT_BRANCH == "main":
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
else:
    TELEGRAM_TOKEN = os.getenv("TEST_TELEGRAM_TOKEN")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Остальные ключи
SUPABASE_URL = "https://iztwzgewaxzdmcbqkxlm.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_APIKEY")
SUPABASE_RPC_FUNCTION = "match_documents"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "text-embedding-3-small"
