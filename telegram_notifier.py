import os
import httpx
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEFAULT_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


async def send_telegram_message(chat_id: str, text: str):
    if not BOT_TOKEN or not chat_id:
        print("Telegram not configured. Skipping notification.")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(url, json=payload)
            r.raise_for_status()
        except Exception as e:
            print("Failed to send telegram message:", e)
