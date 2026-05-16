import requests
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise SystemExit("Faltan TELEGRAM_BOT_TOKEN y/o TELEGRAM_CHAT_ID")

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

r = requests.post(url, data={
    "chat_id": CHAT_ID,
    "text": "✅ Prueba Telegram desde bot BTC"
})

print(r.status_code)
print(r.text)
