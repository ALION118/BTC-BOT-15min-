import requests

TOKEN = "8737427032:AAGx3rwTYONW5eAfIOGkpz4jnKkisLrCmB8"
CHAT_ID = "132352118"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

r = requests.post(url, data={
    "chat_id": CHAT_ID,
    "text": "✅ Prueba Telegram desde bot BTC"
})

print(r.status_code)
print(r.text)
