# telegram_notifier.py
import telebot
import os
from datetime import datetime

# Конфигурация
TELEGRAM_BOT_TOKEN = '8468371879:AAEvloU6H47kNyV3OyVeUKX2zYz5HG_T4zo'
TELEGRAM_CHAT_IDS = ['839519148', '1448610598']  # Может быть несколько chat_id

# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def send_contact_notification(contact_data):
    """Отправка уведомления о новой заявке"""
    try:
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        text = f"""
📬 *НОВОЕ ОБРАЩЕНИЕ С САЙТА*

*Имя:* {contact_data.get('name', 'Не указано')}
*Email:* `{contact_data.get('email', 'Не указан')}`
*Время:* {timestamp}

*Сообщение:*
{contact_data.get('message', 'Без текста')}
        """.strip()

        success_count = 0
        for chat_id in TELEGRAM_CHAT_IDS:
            try:
                bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                success_count += 1
                print(f"✅ Уведомление отправлено в чат {chat_id}")
            except Exception as e:
                print(f"❌ Ошибка отправки в {chat_id}: {e}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Общая ошибка при отправке в Telegram: {e}")
        return False

def send_order_notification(order_data):
    """Отправка уведомления о новом заказе"""
    try:
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        text = f"""
💰 *НОВЫЙ ЗАКАЗ*

*Заказ:* #{order_data.get('order_id', 'N/A')}
*Товар:* {order_data.get('item_id', 'N/A')}
*Сумма:* {order_data.get('amount', 0)} ₽
*Имя:* {order_data.get('name', 'Не указано')}
*Телефон:* `{order_data.get('phone', 'Не указан')}`
*Email:* `{order_data.get('email', 'Не указан')}`
*Время:* {timestamp}
        """.strip()

        success_count = 0
        for chat_id in TELEGRAM_CHAT_IDS:
            try:
                bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode='Markdown'
                )
                success_count += 1
            except Exception as e:
                print(f"❌ Ошибка отправки заказа в {chat_id}: {e}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Общая ошибка при отправке заказа: {e}")
        return False
    
def send_custom_order_notification(order_data):
    """Отправка уведомления о индивидуальном заказе"""
    try:
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        # Формируем текст сообщения
        text = f"""
🎯 *НОВЫЙ ИНДИВИДУАЛЬНЫЙ ЗАКАЗ*

*Заказ:* #{order_data.get('order_id', 'N/A')}
*ФИО:* {order_data.get('fullName', 'Не указано')}
*Телефон:* `{order_data.get('phone', 'Не указан')}`
*Email:* `{order_data.get('email', 'Не указан')}`
*Telegram:* {order_data.get('telegram', 'Не указан') or 'Не указан'}
*Время:* {timestamp}

*Описание заказа:*
{order_data.get('orderDescription', 'Без описания')}
        """.strip()

        success_count = 0
        for chat_id in TELEGRAM_CHAT_IDS:
            try:
                bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                success_count += 1
                print(f"✅ Уведомление о индивидуальном заказе отправлено в чат {chat_id}")
            except Exception as e:
                print(f"❌ Ошибка отправки индивидуального заказа в {chat_id}: {e}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Общая ошибка при отправке индивидуального заказа: {e}")
        return False