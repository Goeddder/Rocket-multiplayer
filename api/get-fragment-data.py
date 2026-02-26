from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from Buy_start.client import FragmentClient

app = FastAPI()

# Это лечит "Ошибку сети" (разрешает браузеру забирать данные)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/get-fragment-data")
async def get_data(username: str = Body(..., embed=True), amount: int = Body(..., embed=True)):
    try:
        client = FragmentClient()
        # Ищем получателя
        recipient = await client.fetch_recipient(username)
        if not recipient:
            return {"ok": False, "error": "User not found"}
        
        # Получаем ID сессии покупки
        req_id = await client.fetch_req_id(recipient, amount)
        if not req_id:
            return {"ok": False, "error": "Fragment session error"}
            
        # Забираем адрес, точную сумму в нано и PAYLOAD (комментарий)
        address, amount_nano, payload = await client.fetch_buy_link(recipient, req_id, amount)
        
        return {
            "ok": True,
            "address": address,
            "amount_ton": float(amount_nano) / 1e9,
            "payload": payload
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
