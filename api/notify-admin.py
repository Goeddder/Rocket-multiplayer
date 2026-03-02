import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ТВОИ ДАННЫЕ
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

    # --- ОБРАБОТКА WEBHOOK ОТ TELEGRAM (Сообщения, /start, Фото) ---
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        username = msg.get("from", {}).get("username")
        user_mention = f"@{username}" if username else msg.get("from", {}).get("first_name", "Клиент")

        if "text" in msg and msg["text"] == "/start":
            welcome_text = "👋 Магазин SkruchStars открыт! Нажми кнопку ниже:"
            kb = {"inline_keyboard": [[{"text": "🚀 Окрыть Магазин", "web_app": {"url": "https://rocket-multiplayer.vercel.app"}}]]}
            send_tg("sendMessage", {"chat_id": chat_id, "text": welcome_text, "reply_markup": kb})
            return jsonify({"ok": True})

        # Пересылка чеков и отзывов админу
        if chat_id != ADMIN_ID:
            has_photo = "photo" in msg
            is_text = "text" in msg
            
            if has_photo or is_text:
                send_tg("sendMessage", {
                    "chat_id": ADMIN_ID, 
                    "text": f"📣 **Новое сообщение от:** {user_mention} (ID: `{chat_id}`)",
                    "parse_mode": "Markdown"
                })
                send_tg("forwardMessage", {
                    "chat_id": ADMIN_ID,
                    "from_chat_id": chat_id,
                    "message_id": msg["message_id"]
                })
            return jsonify({"ok": True})

    # --- ОБРАБОТКА ЗАКАЗОВ ИЗ WEB APP ---
    
    # А) Заказ Stars
    if data.get("type") == "STARS_PURCHASE":
        user = data.get('user_to_receive', 'unknown')
        stars = data.get('stars', '0')
        client_id = data.get('client_id', 'None')

        admin_text = f"⭐️ **ЗАКАЗ STARS (TON)**\n\n👤 Получатель: @{user}\n💎 Количество: {stars} шт.\nID: `{client_id}`"
        kb = {"inline_keyboard": [
            [{"text": "✅ ВЫПОЛНЕНО", "callback_data": f"done_{client_id}"}],
            [{"text": "❌ ОТКЛОНИТЬ", "callback_data": f"cancel_{client_id}"}]
        ]}
        send_tg("sendMessage", {"chat_id": ADMIN_ID, "text": admin_text, "parse_mode": "Markdown", "reply_markup": kb})
        return jsonify({"ok": True})

    # Б) Заказ TON за ГРН
    if data.get("type") == "TON_PURCHASE_UAH":
        wallet = data.get('wallet', 'None')
        ton_amount = data.get('ton_amount', '0')
        uah_amount = data.get('uah_amount', '0')
        client_id = data.get('client_id', 'None')

        admin_text = (f"💳 **ЗАЯВКА TON (ГРН)**\n\n"
                      f"💰 К оплате: `{uah_amount}`\n"
                      f"💎 К отправке: `{ton_amount} TON`\n"
                      f"🏦 Кошелек: `{wallet}`\n"
                      f"👤 ID: `{client_id}`")
        
        kb = {"inline_keyboard": [
            [{"text": "✅ ОПЛАЧЕНО", "callback_data": f"tondone_{client_id}"}],
            [{"text": "❌ ОТКЛОНИТЬ", "callback_data": f"cancel_{client_id}"}]
        ]}
        send_tg("sendMessage", {"chat_id": ADMIN_ID, "text": admin_text, "parse_mode": "Markdown", "reply_markup": kb})
        
        # Сразу просим клиента скинуть квитанцию
        send_tg("sendMessage", {
            "chat_id": int(client_id), 
            "text": "⚠️ **Заявка принята!**\n\nПожалуйста, отправьте **фото квитанции** об оплате прямо сюда в чат. Мы ждем подтверждения!",
            "parse_mode": "Markdown"
        })
        return jsonify({"ok": True})

    # --- ОБРАБОТКА CALLBACK КНОПОК ---
    if "callback_query" in data:
        cb = data["callback_query"]
        cb_data = cb["data"]
        
        # Кнопка ОТКЛОНИТЬ
        if cb_data.startswith("cancel_"):
            target_id = cb_data.replace("cancel_", "")
            send_tg("sendMessage", {"chat_id": int(target_id), "text": "❌ **Ваша заявка отклонена.**", "parse_mode": "Markdown"})
            send_tg("editMessageText", {"chat_id": ADMIN_ID, "message_id": cb["message"]["message_id"], "text": cb["message"]["text"] + "\n\n🔴 **ОТКЛОНЕНО**"})

        # Кнопка ПОДТВЕРДИТЬ STARS
        elif cb_data.startswith("done_"):
            target_id = cb_data.replace("done_", "")
            send_tg("sendMessage", {"chat_id": int(target_id), "text": "✅ **Звезды зачислены!**", "parse_mode": "Markdown"})
            send_tg("editMessageText", {"chat_id": ADMIN_ID, "message_id": cb["message"]["message_id"], "text": cb["message"]["text"] + "\n\n🟢 **ВЫПОЛНЕНО**"})

        # Кнопка ПОДТВЕРДИТЬ TON
        elif cb_data.startswith("tondone_"):
            target_id = cb_data.replace("tondone_", "")
            send_tg("sendMessage", {"chat_id": int(target_id), "text": "💎 **TON зачислен!** Проверьте кошелек.", "parse_mode": "Markdown"})
            send_tg("editMessageText", {"chat_id": ADMIN_ID, "message_id": cb["message"]["message_id"], "text": cb["message"]["text"] + "\n\n🟢 **ТОН ОТПРАВЛЕН**"})

        send_tg("answerCallbackQuery", {"callback_query_id": cb["id"]})

    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(port=5000)
            
        
