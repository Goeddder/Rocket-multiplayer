import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ТВОИ ОБНОВЛЕННЫЕ ДАННЫЕ
BOT_TOKEN = "8655647282:AAHom6iN4Ar5XY42MuZ4lxG9SmWz16x9maA"
ADMIN_ID = 1471307057
WEB_APP_URL = "https://ТВОЙ-ДОМЕН.vercel.app" # Не забудь вставить свой домен Vercel

def send_tg(method, payload):
    return requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/{method}", json=payload)

# ... далее весь остальной код из прошлого сообщения без изменений ...
