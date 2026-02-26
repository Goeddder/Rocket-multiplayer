import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# КОНФИГУРАЦИЯ
BOT_TOKEN = "8250116983:AAGGgp7aJPFF0IYBfzeoHK7cwx-hi2Zhgkk"
ADMIN_ID = 1471307057
WEB_APP_URL = "https://rocket-multiplayer.vercel.app"

def send_tg(method, payload):
    return requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/{method}", json=payload)

@app.route('/api/notify-admin', methods=['GET', 'POST'])
def handle_all():
    # Если ты просто зашел на страницу через браузер
    if request.method == 'GET':
        return "Бот настроен и готов принимать Webhook!"

    data = request.json
    if not data:
        return jsonify({"error": "No data"}), 400

    # --- ЛОГИКА ДЛЯ САЙТА (Запрос на оплату) ---
    if "user_to_receive" in data:
        user = data.get('user_to_receive', '').replace('@', '')
        stars = data.get('stars', 'Stars')
        price = data.get('amount', '0')
        
        text = f"💰 **НОВЫЙ ЗАКАЗ!**\n\n👤 Клиент: @{user}\n💎 Товар: {stars}\n💸 Цена: {price} TON\n\nНажми кнопку после отправки:"
        kb = {"inline_keyboard": [[{"text": "✅ ОТПРАВИЛ", "callback_data": f"done_{user}"}]]}
        send_tg("sendMessage", {"chat_id": ADMIN_ID, "text": text, "parse_mode": "Markdown", "reply_markup": kb})
        return jsonify({"ok": True})

    # --- ЛОГИКА ДЛЯ БОТА (Webhook сообщения) ---
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")

        if text == "/start":
            welcome_text = "Привет! 👋 Ты в **SkruchStarsBot**.\nЖми кнопку ниже, чтобы купить звезды!"
            kb = {"inline_keyboard": [[{"text": "🚀 КУПИТЬ STARS", "web_app": {"url": WEB_APP_URL}}]]}
            send_tg("sendMessage", {"chat_id": chat_id, "text": welcome_text, "reply_markup": kb})

        elif chat_id != ADMIN_ID:
            send_tg("sendMessage", {"chat_id": chat_id, "text": "Спасибо за отзыв! ❤️"})
            send_tg("copyMessage", {"chat_id": ADMIN_ID, "from_chat_id": chat_id, "message_id": msg["message_id"]})

    # --- ЛОГИКА КНОПОК (Callback) ---
    if "callback_query" in data:
        cb = data["callback_query"]
        cb_data = cb["data"]
        if cb_data.startswith("done_"):
            target_user = cb_data.replace("done_", "")
            send_tg("sendMessage", {"chat_id": f"@{target_user}", "text": "✅ **Звезды зачислены!**\nПожалуйста, оставьте отзыв с фото!"})
            send_tg("answerCallbackQuery", {"callback_query_id": cb["id"], "text": "Готово!"})

    return jsonify({"ok": True})
