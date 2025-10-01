import telebot
import json
import os
from datetime import datetime

TELEGRAM_BOT_TOKEN = '6543210987:AAHd7uX9vK1mN2oP3qR4sT5uV6wX7yZ8aB9'
TELEGRAM_CHAT_IDS = ['123456789', '987654321']

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)

def send_telegram_notification(data):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_IDS:
        print("⚠️ Telegram не настроен")
        return False

    text = (
        "📬 *Новое обращение через сайт!*\n\n"
        f"*Имя:* {data.get('name', '—')}\n"
        f"*Email:* {data.get('email', '—')}\n"
        f"*Сообщение:*\n{data.get('message', '—')}"
    )

    for chat_id in TELEGRAM_CHAT_IDS:
        try:
            bot.send_message(chat_id, text, parse_mode='Markdown')
        except Exception as e:
            print(f"❌ Ошибка при отправке в {chat_id}: {e}")
    return True

def send_telegram_order_notification(order):
    if not TELEGRAM_CHAT_IDS:
        return
    text = (
        "💰 *Новый платёж прошёл успешно!*\n\n"
        f"*Заказ:* {order.get('order_id')}\n"
        f"*Товар:* {order.get('item_id')}\n"
        f"*Сумма:* {order.get('amount')} ₽\n"
        f"*Имя:* {order.get('name')}\n"
        f"*Телефон:* {order.get('phone')}\n"
        f"*Email:* {order.get('email')}"
    )
    for chat_id in TELEGRAM_CHAT_IDS:
        try:
            bot.send_message(chat_id, text, parse_mode='Markdown')
        except:
            pass