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

    # --- 1. ОБРАБОТКА СООБЩЕНИЙ ИЗ ТЕЛЕГРАМА (Webhooks) ---
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        username = msg.get("from", {}).get("username")
        user_mention = f"@{username}" if username else msg.get("from", {}).get("first_name", "Клиент")

        if "text" in msg and msg["text"] == "/start":
            welcome_text = "👋 Магазин SkruchStars открыт! Нажми кнопку ниже, чтобы купить Stars или TON:"
            kb = {"inline_keyboard": [[{"text": "🚀 Окрыть Магазин", "web_app": {"url": "https://rocket-multiplayer.vercel.app"}}]]}
            send_tg("sendMessage", {"chat_id": chat_id, "text": welcome_text, "reply_markup": kb})
            return jsonify({"ok": True})

        # Фильтр отзывов / чеков оплаты
        if chat_id != ADMIN_ID:
            has_photo = "photo" in msg
            is_review = "text" in msg and len(msg["text"]) > 5
            
            if has_photo or is_review:
                send_tg("sendMessage", {
                    "chat_id": ADMIN_ID, 
                    "text": f"📣 **Новое сообщение/отзыв от:** {user_mention} (ID: `{chat_id}`)",
                    "parse_mode": "Markdown"
                })
                send_tg("forwardMessage", {
                    "chat_id": ADMIN_ID,
                    "from_chat_id": chat_id,
                    "message_id": msg["message_id"]
                })
            return jsonify({"ok": True})

    # --- 2. ОБРАБОТКА ЗАКАЗОВ ИЗ WEB APP (JSON POST) ---
    
    # А) Покупка Stars (через TON)
    if data.get("type") == "STARS_PURCHASE" or "user_to_receive" in data:
        user = data.get('user_to_receive', 'unknown')
        stars = data.get('stars', 'Stars')
        client_id = data.get('client_id') or data.get('client_chat_id', 'None')

        admin_text = f"⭐️ **НОВЫЙ ЗАКАЗ STARS!**\n\n👤 Получатель: @{user.replace('@','')}\n💎 Количество: {stars} шт.\n💳 Оплата: TON (проверь кошелек)"
        kb = {"inline_keyboard": [[{"text": "✅ ОТПРАВИЛ", "callback_data": f"done_{client_id}"}]]}
        send_tg("sendMessage", {"chat_id": ADMIN_ID, "text": admin_text, "parse_mode": "Markdown", "reply_markup": kb})
        return jsonify({"ok": True})

    # Б) Покупка TON (за ГРН через карту)
    if data.get("type") == "TON_PURCHASE_UAH":
        wallet = data.get('wallet', 'Не указан')
        ton_amount = data.get('ton_amount', '0')
        uah_amount = data.get('uah_amount', '0')
        client_id = data.get('client_id', 'None')

        admin_text = (f"💳 **ЗАЯВКА: КУПИТЬ TON ЗА ГРН**\n\n"
                      f"💰 Сумма к получению: `{uah_amount}`\n"
                      f"💎 Отправить клиенту: `{ton_amount} TON`\n"
                      f"🏦 Кошелек клиента: `{wallet}`\n"
                      f"👤 ID клиента: `{client_id}`\n\n"
                      f"⚠️ Жди фото чека от клиента!")
        
        kb = {"inline_keyboard": [[{"text": "✅ TON ОТПРАВЛЕН", "callback_data": f"tondone_{client_id}"}]]}
        send_tg("sendMessage", {"chat_id": ADMIN_ID, "text": admin_text, "parse_mode": "Markdown", "reply_markup": kb})
        return jsonify({"ok": True})

    # --- 3. ОБРАБОТКА КНОПОК "ГОТОВО" ---
    if "callback_query" in data:
        cb = data["callback_query"]
        cb_data = cb["data"]
        
        # Для Звезд
        if cb_data.startswith("done_"):
            target_id = cb_data.replace("done_", "")
            msg_to_client = "✅ **Звёзды зачислены!**\n\nБудем благодарны за отзыв! Пришлите фото и текст **одним сообщением** 👇"
            send_tg("sendMessage", {"chat_id": int(target_id), "text": msg_to_client, "parse_mode": "Markdown"})
            send_tg("answerCallbackQuery", {"callback_query_id": cb["id"], "text": "Клиент уведомлен!"})
            
        # Для ТОН
        if cb_data.startswith("tondone_"):
            target_id = cb_data.replace("tondone_", "")
            msg_to_client = "💎 **TON зачислен на ваш кошелек!**\n\nСпасибо за покупку! Оставьте отзыв, если всё понравилось."
            send_tg("sendMessage", {"chat_id": int(target_id), "text": msg_to_client, "parse_mode": "Markdown"})
            send_tg("answerCallbackQuery", {"callback_query_id": cb["id"], "text": "Клиент уведомлен!"})

    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(port=5000)
        
