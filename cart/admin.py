# cart/admin.py
from django.contrib import admin
from .models import CartItem, Order

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'product', 'quantity', 'date_added')
    list_filter = ('date_added',)
    search_fields = ('session_id', 'product__name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'phone')
    readonly_fields = ('items',)