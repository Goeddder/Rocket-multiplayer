import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# КОНФИГУРАЦИЯ
BOT_TOKEN = "8655647282:AAHom6iN4Ar5XY42MuZ4lxG9SmWz16x9maA"
ADMIN_ID = 1471307057
WEB_APP_URL = "https://rocket-multiplayer.vercel.app"

def send_tg(method, payload):
    return requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/{method}", json=payload)

@app.route('/api/notify-admin', methods=['POST'])
def handle_all():
    data = request.json
    if not data:
        return jsonify({"error": "No data"}), 400

    # --- ЛОГИКА ДЛЯ САЙТА (Запрос на оплату) ---
    if "user_to_receive" in data:
        user = data.get('user_to_receive', '').replace('@', '')
        stars = data.get('stars', 'Stars')
        price = data.get('amount', '0')
        wallet = data.get('sender', 'Неизвестен')
        
        text = (
            f"💰 **НОВЫЙ ЗАКАЗ!**\n\n"
            f"👤 Клиент: @{user}\n"
            f"💎 Товар: {stars}\n"
            f"💸 Цена: {price} TON\n"
            f"👛 Кошелек: `{wallet}`\n\n"
            f"Отправь звезды и нажми кнопку ниже, чтобы бот запросил отзыв:"
        )
        kb = {"inline_keyboard": [[{"text": "✅ ОТПРАВИЛ", "callback_data": f"done_{user}"}]]}
        send_tg("sendMessage", {"chat_id": ADMIN_ID, "text": text, "parse_mode": "Markdown", "reply_markup": kb})
        return jsonify({"ok": True})

    # --- ЛОГИКА ДЛЯ БОТА (Webhook сообщения) ---
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")

        # Обработка /start
        if text == "/start":
            user_name = msg["from"].get("first_name", "Друг")
            welcome_text = (
                f"Привет, {user_name}! 👋\n\n"
                f"Ты попал в официального бота **SkruchStarsBot**.\n"
                f"Здесь можно купить Telegram Stars максимально выгодно через TON!"
            )
            kb = {"inline_keyboard": [[{"text": "🚀 КУПИТЬ STARS", "web_app": {"url": WEB_APP_URL}}]]}
            send_tg("sendMessage", {"chat_id": chat_id, "text": welcome_text, "reply_markup": kb})

        # Пересылка отзыва админу (если пишет не админ)
        elif chat_id != ADMIN_ID:
            username = msg["from"].get("username", "Скрыт")
            send_tg("sendMessage", {"chat_id": chat_id, "text": "Спасибо за отзыв! ❤️ Он передан администратору."})
            send_tg("copyMessage", {"chat_id": ADMIN_ID, "from_chat_id": chat_id, "message_id": msg["message_id"]})
            send_tg("sendMessage", {"chat_id": ADMIN_ID, "text": f"👆 Выше — отзыв от @{username}"})

    # --- ЛОГИКА КНОПОК (Callback) ---
    if "callback_query" in data:
        cb = data["callback_query"]
        cb_data = cb["data"]
        
        if cb_data.startswith("done_"):
            target_user = cb_data.replace("done_", "")
            client_text = (
                f"✅ **Успешно!**\n\n"
                f"Звезды зачислены на ваш аккаунт.\n\n"
                f"Пожалуйста, оставьте отзыв (текст + фото) прямо здесь. "
                f"Или напишите 'Пропустить', если не хотите."
            )
            
            # Отправка уведомления клиенту
            res = send_tg("sendMessage", {"chat_id": f"@{target_user}", "text": client_text, "parse_mode": "Markdown"})
            
            if res.status_code == 200:
                send_tg("answerCallbackQuery", {"callback_query_id": cb["id"], "text": "Клиент уведомлен!"})
                send_tg("editMessageText", {
                    "chat_id": ADMIN_ID, 
                    "message_id": cb["message"]["message_id"], 
                    "text": f"✅ Заказ для @{target_user} выполнен и подтвержден!"
                })
            else:
                send_tg("answerCallbackQuery", {
                    "callback_query_id": cb["id"], 
                    "text": "Ошибка: клиент не нажал /start в боте!"
                })

    return jsonify({"ok": True})
