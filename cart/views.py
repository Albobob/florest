from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from catalog.models import Product
from django.views.generic import TemplateView
from django.shortcuts import render
from django.views.decorators.http import require_POST
from .models import CartItem, Order, OrderItem
import json
import requests
from django.conf import settings

class CartView(TemplateView):
    template_name = 'cart/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем корзину из сессии
        cart = self.request.session.get('cart', {})

        # Получаем продукты
        products = Product.objects.filter(id__in=cart.keys())

        # Формируем список товаров с количеством и общей ценой
        cart_items = []
        total_items = 0
        for product in products:
            quantity = cart.get(str(product.id), 0)
            total_price = product.price * quantity
            total_items += quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': total_price,
            })

        context['cart_items'] = cart_items
        context['total_price'] = sum(item['total_price'] for item in cart_items)
        context['total_items'] = total_items

        return context

def get_cart_data(request):
    cart = request.session.get('cart', {})
    total_items = sum(int(quantity) for quantity in cart.values())
    return total_items

def cart_view(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = []
    total = 0
    for product in products:
        quantity = cart.get(str(product.id), 0)
        total_price = product.price * quantity
        total += total_price
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': total_price,
        })
    
    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Получаем корзину из сессии
    cart = request.session.get('cart', {})
    
    # Увеличиваем количество товара в корзине
    cart[str(product.id)] = cart.get(str(product.id), 0) + 1
    
    # Сохраняем корзину в сессии
    request.session['cart'] = cart
    request.session.modified = True
    
    # Подсчитываем общее количество товаров
    total_items = sum(int(quantity) for quantity in cart.values())
    
    return JsonResponse({
        'status': 'success',
        'message': f'"{product.name}" добавлен в корзину',
        'cart_count': total_items
    })

@require_POST
def update_cart(request):
    try:
        data = json.loads(request.body)
        product_id = str(data.get('item_id'))
        quantity = int(data.get('quantity'))
        
        # Get the cart from session
        cart = request.session.get('cart', {})
        
        # Get the product
        product = get_object_or_404(Product, id=product_id)
        
        if quantity > 0:
            # Update quantity
            cart[product_id] = quantity
        else:
            # Remove item if quantity is 0
            if product_id in cart:
                del cart[product_id]
        
        # Save cart back to session
        request.session['cart'] = cart
        request.session.modified = True
        
        # Calculate totals
        item_total = product.price * quantity if quantity > 0 else 0
        cart_total = sum(
            get_object_or_404(Product, id=pid).price * qty 
            for pid, qty in cart.items()
        )
        
        return JsonResponse({
            'status': 'success',
            'item_total': item_total,
            'total': cart_total,
            'cart_count': sum(cart.values())
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

def send_telegram_notification(order):
    if hasattr(settings, 'TELEGRAM_BOT_TOKEN') and hasattr(settings, 'TELEGRAM_CHAT_ID'):
        message = f"""
🌱 Новый заказ #{order.id}!

Клиент: {order.name}
Телефон: {order.phone}
Email: {order.email}

Товары:
"""
        for item in order.items.all():
            message += f"- {item.product.name} x{item.quantity} ({item.price * item.quantity} ₽)\n"
        
        message += f"\nИтого: {order.total_amount} ₽"
        
        try:
            requests.post(
                f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage',
                json={
                    'chat_id': settings.TELEGRAM_CHAT_ID,
                    'text': message,
                    'parse_mode': 'HTML'
                }
            )
        except Exception as e:
            print(f"Ошибка отправки уведомления в Telegram: {e}")

@require_POST
def place_order(request):
    data = json.loads(request.body)
    cart = request.session.get('cart', {})
    
    if not cart:
        return JsonResponse({
            'status': 'error',
            'message': 'Ваша корзина пуста'
        })
    
    # Получаем продукты и считаем общую сумму
    products = Product.objects.filter(id__in=cart.keys())
    total = 0
    order_items = []
    
    for product in products:
        quantity = cart.get(str(product.id), 0)
        total += product.price * quantity
        order_items.append({
            'product': product,
            'quantity': quantity,
            'price': product.price
        })
    
    order = Order.objects.create(
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address'),
        total_amount=total
    )
    
    for item in order_items:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            price=item['price'],
            quantity=item['quantity']
        )
    
    # Очищаем корзину
    request.session['cart'] = {}
    request.session.modified = True
    
    # Отправляем уведомление в Telegram
    send_telegram_notification(order)
    
    return JsonResponse({
        'status': 'success',
        'message': 'Заказ успешно оформлен',
        'order_id': order.id
    })