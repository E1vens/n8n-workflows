import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

SUPABASE_URL = "https://iztwzgewaxzdmcbqkxlm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml6dHd6Z2V3YXh6ZG1jYnFreGxtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxMTYxOTEsImV4cCI6MjA2NDY5MjE5MX0.7_9DiWDygaPlqDf2hopwt3dag3LoS_b9UV91_7UKxjA"
SUPABASE_RPC_FUNCTION = "match_documents"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "text-embedding-3-small"
