import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ТВОИ ОБНОВЛЕННЫЕ ДАННЫЕ
BOT_TOKEN = "8250116983:AAGGgp7aJPFF0IYBfzeoHK7cwx-hi2Zhgkk"
ADMIN_ID = 1471307057
WEB_APP_URL = "https://ТВОЙ-ДОМЕН.vercel.app" # Не забудь вставить свой домен Vercel

def send_tg(method, payload):
    return requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/{method}", json=payload)

# ... далее весь остальной код из прошлого сообщения без изменений ...
