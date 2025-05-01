# cart/admin.py
from django.contrib import admin
from .models import CartItem, Order, OrderItem, TelegramNotification
import requests
from django.conf import settings

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity')
    can_delete = False

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'product', 'quantity', 'date_added')
    list_filter = ('date_added',)
    search_fields = ('session_id', 'product__name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at', 'total_amount')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Customer Information', {
            'fields': ('name', 'email', 'phone', 'address')
        }),
        ('Order Details', {
            'fields': ('status', 'total_amount', 'created_at', 'updated_at')
        }),
    )

@admin.register(TelegramNotification)
class TelegramNotificationAdmin(admin.ModelAdmin):
    list_display = ('get_display_name', 'chat_id', 'username', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('chat_id', 'username', 'first_name')
    readonly_fields = ('chat_id', 'username', 'first_name', 'created_at', 'last_checked')
    actions = ['activate_notifications', 'deactivate_notifications']
    
    def get_display_name(self, obj):
        return obj.first_name or obj.username or obj.chat_id
    get_display_name.short_description = 'Имя'

    def activate_notifications(self, request, queryset):
        updated = queryset.update(is_active=True)
        
        # Отправляем уведомление каждому активированному пользователю
        for notification in queryset:
            try:
                requests.post(
                    f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage',
                    json={
                        'chat_id': notification.chat_id,
                        'text': (
                            "🎉 Поздравляем! Ваш запрос на получение уведомлений одобрен.\n"
                            "Теперь вы будете получать уведомления о новых заказах."
                        ),
                        'parse_mode': 'HTML'
                    }
                )
            except Exception as e:
                print(f"Error sending activation notification: {e}")
        
        self.message_user(request, f'Активировано {updated} подписчиков')
    activate_notifications.short_description = "✅ Активировать выбранные уведомления"

    def deactivate_notifications(self, request, queryset):
        updated = queryset.update(is_active=False)
        
        # Отправляем уведомление каждому деактивированному пользователю
        for notification in queryset:
            try:
                requests.post(
                    f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage',
                    json={
                        'chat_id': notification.chat_id,
                        'text': (
                            "❌ Ваши уведомления были деактивированы администратором.\n"
                            "Вы больше не будете получать уведомления о новых заказах."
                        ),
                        'parse_mode': 'HTML'
                    }
                )
            except Exception as e:
                print(f"Error sending deactivation notification: {e}")
        
        self.message_user(request, f'Деактивировано {updated} подписчиков')
    deactivate_notifications.short_description = "❌ Деактивировать выбранные уведомления"

    fieldsets = (
        ('Информация о пользователе', {
            'fields': ('first_name', 'username', 'chat_id')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'last_checked'),
            'classes': ('collapse',)
        }),
    )