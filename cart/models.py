# cart/models.py
from django.db import models
from django.contrib.auth.models import User
from catalog.models import Product
from django.core.validators import MinValueValidator

class CartItem(models.Model):
    session_id = models.CharField(max_length=32, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        pass  # Temporarily remove unique_together

    def get_total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x{self.quantity} (Session: {self.session_id})"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('processing', 'Обрабатывается'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]

    name = models.CharField(max_length=200, verbose_name="ФИО")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.TextField(null=True, blank=True, verbose_name="Адрес")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Сумма")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ {self.id} - {self.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def get_total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x{self.quantity} (Заказ: {self.order.id})"

class TelegramNotification(models.Model):
    chat_id = models.CharField(max_length=100, unique=True, verbose_name="Telegram Chat ID")
    username = models.CharField(max_length=100, blank=True, null=True, verbose_name="Username")
    first_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Имя")
    is_active = models.BooleanField(default=False, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    last_checked = models.DateTimeField(auto_now=True, verbose_name="Последняя проверка")

    class Meta:
        verbose_name = "Telegram подписчик"
        verbose_name_plural = "Telegram подписчики"

    def __str__(self):
        name = self.first_name or self.username or self.chat_id
        status = 'Активен' if self.is_active else 'Ожидает подтверждения'
        return f"{name} ({status})"