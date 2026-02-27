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
        
        # Отримуємо нікнейм або ім'я
        username = msg.get("from", {}).get("username")
        user_mention = f"@{username}" if username else msg.get("from", {}).get("first_name", "Клиент")

        # 1. Обробка /start
        if "text" in msg and msg["text"] == "/start":
            welcome_text = "👋 Магазин Stars открыт! Нажми кнопку:"
            kb = {"inline_keyboard": [[{"text": "🚀 КУПИТЬ STARS", "web_app": {"url": "https://rocket-multiplayer.vercel.app"}}]]}
            send_tg("sendMessage", {"chat_id": chat_id, "text": welcome_text, "reply_markup": kb})
            return jsonify({"ok": True})

        # 2. ФІЛЬТР ВІДГУКІВ (Пересилаємо тільки фото або повідомлення з текстом відгуку)
        if chat_id != ADMIN_ID:
            # Перевіряємо, чи є в повідомленні фото або довгий текст (схожий на відгук)
            has_photo = "photo" in msg
            is_review = "text" in msg and len(msg["text"]) > 10
            
            if has_photo or is_review:
                # Спочатку пишемо адміну від кого відгук
                send_tg("sendMessage", {
                    "chat_id": ADMIN_ID, 
                    "text": f"📣 **Новый отзыв от:** {user_mention}",
                    "parse_mode": "Markdown"
                })
                # Пересилаємо сам відгук (фото або текст)
                send_tg("forwardMessage", {
                    "chat_id": ADMIN_ID,
                    "from_chat_id": chat_id,
                    "message_id": msg["message_id"]
                })
            return jsonify({"ok": True})

    # 3. ЗАМОВЛЕННЯ З САЙТУ
    if "user_to_receive" in data:
        user = data.get('user_to_receive', 'unknown')
        stars = data.get('stars', 'Stars')
        price = data.get('amount', '0')
        client_id = data.get('client_chat_id', 'None')

        admin_text = f"💰 **НОВЫЙ ЗАКАЗ!**\n\n👤 Получатель: {user}\n💎 Товар: {stars}\n💸 Цена: {price} TON"
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
                msg_to_client = "✅ **Звёзды зачислены!**\n\nБудем благодарны за отзыв! Пришлите фото и текст **одним сообщением** 👇"
                send_tg("sendMessage", {"chat_id": int(target_id), "text": msg_to_client, "parse_mode": "Markdown"})
                send_tg("answerCallbackQuery", {"callback_query_id": cb["id"], "text": "Готово!"})

    return jsonify({"ok": True})
