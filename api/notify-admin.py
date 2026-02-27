import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = "8250116983:AAGGgp7aJPFF0IYBfzeoHK7cwx-hi2Zhgkk"
ADMIN_ID = 1471307057

def send_tg(method, payload):
    return requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/{method}", json=payload)

@app.route('/api/notify-admin', methods=['POST', 'GET'])
def handle_all():
    if request.method == 'GET':
        return "Backend is running!"

    data = request.json
    if not data: return jsonify({"ok": False})

    # 1. КОЛИ КЛІЄНТ ТИСНЕ "ОПЛАТИТИ" НА САЙТІ
    if "user_to_receive" in data:
        user = data.get('user_to_receive', 'unknown')
        stars = data.get('stars', 'Stars')
        price = data.get('amount', '0')
        # Спроба отримати chat_id, якщо він переданий з сайту
        client_chat_id = data.get('client_chat_id', '') 

        text = f"💰 **НОВИЙ ЗАКАЗ!**\n\n👤 Клиент: {user}\n💎 Товар: {stars}\n💸 Цена: {price} TON"
        # Зберігаємо ID клієнта прямо в кнопку, щоб бот знав кому відповісти
        kb = {"inline_keyboard": [[{"text": "✅ ОТПРАВИЛ", "callback_data": f"done_{client_chat_id}"}]]}
        
        send_tg("sendMessage", {"chat_id": ADMIN_ID, "text": text, "parse_mode": "Markdown", "reply_markup": kb})
        return jsonify({"ok": True})

    # 2. КОЛИ ТИ ТИСНЕШ КНОПКУ "✅ ОТПРАВИЛ"
    if "callback_query" in data:
        cb = data["callback_query"]
        cb_data = cb["data"]
        
        if cb_data.startswith("done_"):
            target_id = cb_data.replace("done_", "")
            
            if target_id and target_id != "None":
                # Надсилаємо повідомлення клієнту
                msg_to_client = "✅ **Звезды зачислены!**\n\nБудем очень благодарны за отзыв с фото! ❤️"
                send_tg("sendMessage", {"chat_id": target_id, "text": msg_to_client, "parse_mode": "Markdown"})
                
                # Повідомляємо тебе, що все ок
                send_tg("answerCallbackQuery", {"callback_query_id": cb["id"], "text": "Клиент уведомлен!"})
            else:
                send_tg("answerCallbackQuery", {"callback_query_id": cb["id"], "text": "Ошибка: ID клиента не найден. Напиши ему вручную."})

    return jsonify({"ok": True})
