from django.core.management.base import BaseCommand
import requests
from django.conf import settings

class Command(BaseCommand):
    help = 'Set Telegram webhook URL'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='Webhook URL (e.g., https://your-domain.com/cart/webhook/telegram/)')

    def handle(self, *args, **options):
        webhook_url = options['url']
        
        try:
            # Сначала удалим текущий вебхук
            delete_response = requests.post(
                f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/deleteWebhook'
            )
            if delete_response.status_code == 200:
                self.stdout.write("Successfully deleted old webhook")
            
            # Установим новый вебхук
            response = requests.post(
                f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook',
                json={'url': webhook_url}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    self.stdout.write(self.style.SUCCESS(f"Successfully set webhook to: {webhook_url}"))
                    self.stdout.write(f"Description: {result.get('description', 'No description')}")
                else:
                    self.stdout.write(self.style.ERROR(f"Error: {result.get('description')}"))
            else:
                self.stdout.write(self.style.ERROR(f"Error: HTTP {response.status_code}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error setting webhook: {str(e)}")) 