from fastapi import FastAPI, Body
from Buy_start.client import FragmentClient

app = FastAPI()

@app.post("/api/get-fragment-data")
async def get_data(username: str = Body(..., embed=True), amount: int = Body(..., embed=True)):
    client = FragmentClient()
    recipient = await client.fetch_recipient(username)
    if not recipient: return {"ok": False}
    
    req_id = await client.fetch_req_id(recipient, amount)
    address, amount_nano, payload = await client.fetch_buy_link(recipient, req_id, amount)
    
    return {
        "ok": True,
        "address": address,
        "amount_ton": float(amount_nano) / 1e9,
        "payload": payload
    }
