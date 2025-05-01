from django.core.management.base import BaseCommand
import requests
from django.conf import settings

class Command(BaseCommand):
    help = 'Check Telegram webhook settings'

    def handle(self, *args, **options):
        try:
            response = requests.get(
                f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getWebhookInfo'
            )
            webhook_info = response.json()
            
            self.stdout.write("\nTelegram Webhook Information:")
            self.stdout.write("=" * 50)
            
            if response.status_code == 200:
                if webhook_info.get('ok'):
                    result = webhook_info.get('result', {})
                    self.stdout.write(f"URL: {result.get('url', 'Not set')}")
                    self.stdout.write(f"Has custom certificate: {result.get('has_custom_certificate', False)}")
                    self.stdout.write(f"Pending update count: {result.get('pending_update_count', 0)}")
                    self.stdout.write(f"Last error date: {result.get('last_error_date', 'None')}")
                    self.stdout.write(f"Last error message: {result.get('last_error_message', 'None')}")
                    self.stdout.write(f"Max connections: {result.get('max_connections', 'Default')}")
                    
                    if not result.get('url'):
                        self.stdout.write(self.style.WARNING("\nWarning: Webhook URL is not set!"))
                else:
                    self.stdout.write(self.style.ERROR(f"\nError: {webhook_info.get('description')}"))
            else:
                self.stdout.write(self.style.ERROR(f"\nError: HTTP {response.status_code}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nError checking webhook: {str(e)}")) 