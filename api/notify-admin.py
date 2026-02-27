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

    # --- ОБРАБОТКА КОМАНД ТЕЛЕГРАМА ---
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")

        if text == "/start":
            # Ответ пользователю с кнопкой магазина
            welcome_text = "👋 Привет! Нажми на кнопку ниже, чтобы открыть магазин:"
            kb = {
                "inline_keyboard": [[
                    {"text": "🚀 КУПИТЬ STARS", "web_app": {"url": "https://rocket-multiplayer.vercel.app"}}
                ]]
            }
            send_tg("sendMessage", {"chat_id": chat_id, "text": welcome_text, "reply_markup": kb})
            return jsonify({"ok": True})

    # --- ОБРАБОТКА УВЕДОМЛЕНИЙ С САЙТА ---
    if "user_to_receive" in data:
        user = data.get('user_to_receive', 'unknown')
        stars = data.get('stars', 'Stars')
        price = data.get('amount', '0')
        
        # Мы сохраняем chat_id клиента в callback_data кнопки админа
        client_id = data.get('client_chat_id', 'None')

        admin_text = f"💰 **НОВЫЙ ЗАКАЗ!**\n\n👤 Клиент: {user}\n💎 Товар: {stars}\n💸 Цена: {price} TON"
        kb = {"inline_keyboard": [[{"text": "✅ ОТПРАВИЛ", "callback_data": f"done_{client_id}"}]]}
        
        send_tg("sendMessage", {"chat_id": ADMIN_ID, "text": admin_text, "parse_mode": "Markdown", "reply_markup": kb})
        return jsonify({"ok": True})

    # --- ОБРАБОТКА НАЖАТИЯ КНОПКИ "ОТПРАВИЛ" ---
    if "callback_query" in data:
        cb = data["callback_query"]
        cb_data = cb["data"]
        
        if cb_data.startswith("done_"):
            target_id = cb_data.replace("done_", "")
            if target_id != "None" and target_id.isdigit():
                msg_to_client = "✅ **Звезды зачислены!**\n\nБудем очень благодарны за отзыв с фото! ❤️"
                send_tg("sendMessage", {"chat_id": int(target_id), "text": msg_to_client, "parse_mode": "Markdown"})
                send_tg("answerCallbackQuery", {"callback_query_id": cb["id"], "text": "Клиент уведомлен!"})
            else:
                send_tg("answerCallbackQuery", {"callback_query_id": cb["id"], "text": "Ошибка: ID клиента неизвестен."})

    return jsonify({"ok": True})
