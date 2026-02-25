from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from Buy_start.client import FragmentClient
import logging

# Настройка логирования, чтобы видеть ошибки в панели Vercel
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Разрешаем запросы с твоего фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/get-fragment-data")
async def get_fragment_data(
    username: str = Body(..., embed=True), 
    amount: int = Body(..., embed=True)
):
    try:
        # Инициализируем клиент Fragment
        client = FragmentClient()
        
        # 1. Ищем получателя на Fragment
        logger.info(f"Searching recipient: {username}")
        recipient = await client.fetch_recipient(username)
        
        if not recipient:
            logger.error(f"Recipient {username} not found")
            return {"ok": False, "error": "User not found on Fragment"}

        # 2. Получаем внутренний ID запроса для покупки звезд
        logger.info(f"Fetching ReqID for amount: {amount}")
        req_id = await client.fetch_req_id(recipient, amount)
        
        if not req_id:
            logger.error("Failed to get ReqID")
            return {"ok": False, "error": "Fragment session error or invalid amount"}

        # 3. Получаем финальные данные для перевода (адрес, сумма, полезная нагрузка)
        logger.info(f"Fetching buy link data...")
        address, amount_nano, payload = await client.fetch_buy_link(recipient, req_id, amount)

        if not address or not payload:
            logger.error("Failed to fetch buy link details")
            return {"ok": False, "error": "Could not generate payment data"}

        # Возвращаем данные на фронтенд
        return {
            "ok": True,
            "address": address,
            "amount_ton": float(amount_nano) / 1e9, # Конвертируем нанотоны в TON для отображения
            "payload": payload,
            "username": username,
            "stars": amount
        }

    except Exception as e:
        logger.exception(f"Global error in API: {str(e)}")
        return {"ok": False, "error": "Internal Server Error"}

# Если Vercel требует точку входа index
@app.get("/")
async def root():
    return {"status": "API is running"}
