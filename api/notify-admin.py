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

    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        
        # 1. Обробка /start
        if "text" in msg and msg["text"] == "/start":
            welcome_text = "👋 Магазин Stars відкритий! Натисніть кнопку нижче:"
            kb = {"inline_keyboard": [[{"text": "🚀 КУПИТЬ STARS", "web_app": {"url": "https://rocket-multiplayer.vercel.app"}}]]}
            send_tg("sendMessage", {"chat_id": chat_id, "text": welcome_text, "reply_markup": kb})
            return jsonify({"ok": True})

        # 2. ПЕРЕСИЛАННЯ ВІДГУКУ (ФОТО АБО ТЕКСТ)
        if chat_id != ADMIN_ID:
            # Якщо клієнт надіслав фото (з підписом або без)
            # Пересилаємо саме повідомлення адміну
            send_tg("forwardMessage", {
                "chat_id": ADMIN_ID,
                "from_chat_id": chat_id,
                "message_id": msg["message_id"]
            })
            
            # Щоб бот не писав "Дякую" на кожне слово, ми можемо це закоментувати
            # Або залишити тільки для першого повідомлення.
            # На Vercel важко зробити затримку 1 хв без бази даних, 
            # тому ми просто приберемо авто-відповідь клієнту, щоб він не спамив у відповідь.
            return jsonify({"ok": True})

    # 3. ЗАМОВЛЕННЯ З САЙТУ
    if "user_to_receive" in data:
        user = data.get('user_to_receive', 'unknown')
        stars = data.get('stars', 'Stars')
        price = data.get('amount', '0')
        client_id = data.get('client_chat_id', 'None')

        admin_text = f"💰 **НОВИЙ ЗАКАЗ!**\n\n👤 Клиент: {user}\n💎 Товар: {stars}\n💸 Цена: {price} TON"
        kb = {"inline_keyboard": [[{"text": "✅ ОТПРАВИЛ", "callback_data": f"done_{client_id}"}]]}
        send_tg("sendMessage", {"chat_id": ADMIN_ID, "text": admin_text, "parse_mode": "Markdown", "reply_markup": kb})
        return jsonify({"ok": True})

    # 4. КНОПКА "ОТПРАВИЛ"
    if "callback_query" in data:
        cb = data["callback_query"]
        cb_data = cb["data"]
        if cb_data.startswith("done_"):
            target_id = cb_data.replace("done_", "")
            if target_id.isdigit():
                # Просимо надіслати ВІДГУК ОДНИМ ПОВІДОМЛЕННЯМ
                msg_to_client = "✅ **Звёзды зачислены!**\n\nБудем благодарны за отзыв! Пожалуйста, пришлите **фото и текст одним сообщением** 👇"
                send_tg("sendMessage", {"chat_id": int(target_id), "text": msg_to_client, "parse_mode": "Markdown"})
                send_tg("answerCallbackQuery", {"callback_query_id": cb["id"], "text": "Готово!"})

    return jsonify({"ok": True})
