from fastapi import FastAPI, Body
import httpx

app = FastAPI()

# ЗАПОЛНИ ЭТИ ДАННЫЕ:
BOT_TOKEN = "8250116983:AAGGgp7aJPFF0IYBfzeoHK7cwx-hi2Zhgkk"
ADMIN_ID = "1471307057"

@app.post("/api/notify-admin")
async def notify(data: dict = Body(...)):
    msg = (
        "🔔 **НОВЫЙ ЗАКАЗ ЗВЕЗД!**\n\n"
        f"👤 Кому отправить: {data['user_to_receive']}\n"
        f"⭐️ Количество: {data['stars']} шт.\n"
        f"💰 Оплачено: {data['amount']} TON\n"
        f"👛 Кошелек отправителя: `{data['sender']}`"
    )
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, data={"chat_id": ADMIN_ID, "text": msg, "parse_mode": "Markdown"})
    
    return {"ok": True}
    