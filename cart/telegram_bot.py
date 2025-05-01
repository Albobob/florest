import requests
from django.conf import settings
from .models import TelegramNotification, Order
import logging

logger = logging.getLogger(__name__)

def handle_check_command(message):
    """Handle the /check command and store the user's chat ID"""
    logger.info("Received /check command with message: %s", message)
    
    chat_id = message.get('chat', {}).get('id')
    if not chat_id:
        logger.error("No chat_id found in message")
        return
    
    logger.info("Processing /check for chat_id: %s", chat_id)
    
    # Get user information from message
    username = message.get('from', {}).get('username')
    first_name = message.get('from', {}).get('first_name')
    
    logger.info("User info - username: %s, first_name: %s", username, first_name)
    
    try:
        # Create or update the TelegramNotification entry
        notification, created = TelegramNotification.objects.get_or_create(
            chat_id=str(chat_id),
            defaults={
                'is_active': False,
                'username': username,
                'first_name': first_name
            }
        )
        
        if not created:
            # Update user information if it changed
            notification.username = username
            notification.first_name = first_name
            notification.save()
            logger.info("Updated existing notification for chat_id: %s", chat_id)
        else:
            logger.info("Created new notification for chat_id: %s", chat_id)
        
        # Prepare response message
        if created:
            message_text = (
                f"👋 Здравствуйте, {first_name or username or 'уважаемый пользователь'}!\n\n"
                "✅ Ваш запрос на получение уведомлений зарегистрирован.\n"
                "⏳ Пожалуйста, ожидайте подтверждения администратором.\n\n"
                "📝 Ваши данные:\n"
                f"• ID чата: {chat_id}\n"
                f"• Имя: {first_name or 'Не указано'}\n"
                f"• Username: {username or 'Не указан'}"
            )
        else:
            status = "активен" if notification.is_active else "ожидает подтверждения"
            message_text = (
                f"ℹ️ {first_name or username or 'Уважаемый пользователь'}, "
                "ваш запрос уже зарегистрирован!\n\n"
                "📝 Ваши данные:\n"
                f"• ID чата: {chat_id}\n"
                f"• Имя: {first_name or 'Не указано'}\n"
                f"• Username: {username or 'Не указан'}\n"
                f"• Статус: {status}"
            )
        
        logger.info("Sending response message to chat_id: %s", chat_id)
        
        # Send response
        response = requests.post(
            f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage',
            json={
                'chat_id': chat_id,
                'text': message_text,
                'parse_mode': 'HTML'
            }
        )
        response.raise_for_status()  # Проверяем статус ответа
        logger.info("Successfully sent response message")
        
    except Exception as e:
        logger.error("Error in handle_check_command: %s", str(e), exc_info=True)
        # Пытаемся отправить сообщение об ошибке пользователю
        try:
            requests.post(
                f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage',
                json={
                    'chat_id': chat_id,
                    'text': "❌ Произошла ошибка при обработке команды. Пожалуйста, попробуйте позже.",
                    'parse_mode': 'HTML'
                }
            )
        except Exception as send_error:
            logger.error("Error sending error message: %s", str(send_error))

def send_telegram_notification(order):
    """Send notification about new order to approved Telegram chats"""
    if not hasattr(settings, 'TELEGRAM_BOT_TOKEN'):
        return
    
    # Get all active notification subscribers
    active_subscribers = TelegramNotification.objects.filter(is_active=True)
    
    message = f"""
🌱 Новый заказ #{order.id}!

👤 Клиент: {order.name}
📱 Телефон: {order.phone}
📧 Email: {order.email or 'Не указан'}
📍 Адрес: {order.address or 'Не указан'}

🛍️ Товары:
"""
    for item in order.items.all():
        message += f"• {item.product.name} x{item.quantity} = {item.price * item.quantity} ₽\n"
    
    message += f"\n💰 Итого: {order.total_amount} ₽"
    
    # Send to all active subscribers
    for subscriber in active_subscribers:
        try:
            requests.post(
                f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage',
                json={
                    'chat_id': subscriber.chat_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
            )
        except Exception as e:
            print(f"Error sending notification to {subscriber.chat_id}: {e}") 