from django.views import View
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from catalog.models import Product
from django.views.generic import TemplateView
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.middleware.csrf import get_token
from .models import CartItem, Order, OrderItem
from .telegram_bot import handle_check_command, send_telegram_notification
import json
import requests
from django.conf import settings
import logging

# ghjd

logger = logging.getLogger(__name__)

class CartView(TemplateView):
    template_name = 'cart/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем корзину из сессии
        cart = self.request.session.get('cart', {})
        logger.debug(f"Current cart session: {cart}")

        # Получаем продукты
        products = Product.objects.filter(id__in=cart.keys())
        logger.debug(f"Found products: {products}")

        # Формируем список товаров с количеством и общей ценой
        cart_items = []
        total_price = 0
        total_items = 0
        
        for product in products:
            quantity = cart.get(str(product.id), 0)
            logger.debug(f"Product {product.id}: quantity = {quantity}")
            if quantity > 0:  # Добавляем только товары с положительным количеством
                total_price += product.price * quantity
                total_items += quantity
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'total_price': product.price * quantity,
                })

        # Если корзина пуста, явно обнуляем значения
        if not cart_items:
            context['cart_items'] = []
            context['total_price'] = 0
            context['total_items'] = 0
        else:
            context['cart_items'] = cart_items
            context['total_price'] = total_price
            context['total_items'] = total_items

        logger.debug(f"Final cart items: {cart_items}")
        logger.debug(f"Total price: {total_price}")
        logger.debug(f"Total items: {total_items}")

        return context

def get_cart_data(request):
    cart = request.session.get('cart', {})
    total_items = sum(int(quantity) for quantity in cart.values() if int(quantity) > 0)
    return total_items

def cart_page(request):
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
    cart = request.session.get('cart', {})
    cart[str(product.id)] = cart.get(str(product.id), 0) + 1
    request.session['cart'] = cart
    request.session.modified = True
    
    #return JsonResponse({'status': 'success', 'cart_count': sum(int(qty) for qty in cart.values() if int(qty) > 0)})
    return JsonResponse({
        'status': 'success',
        'message': f'Товар «{product.name}» добавлен в корзину',
        'cart_count': total_items
    })

@require_POST
def update_cart(request):
    data = json.loads(request.body)
    product_id = str(data.get('item_id'))
    quantity = int(data.get('quantity'))
    
    # Получаем текущую корзину из сессии
    cart = request.session.get('cart', {})
    
    # Обновляем количество товара
    if quantity > 0:
        cart[product_id] = quantity
    else:
        # Если количество 0, удаляем товар из корзины
        if product_id in cart:
            del cart[product_id]
    
    # Сохраняем обновленную корзину в сессии
    request.session['cart'] = cart
    request.session.modified = True
    
    # Пересчитываем общее количество товаров (только положительные значения)
    total_items = sum(int(qty) for qty in cart.values() if int(qty) > 0)
    
    return JsonResponse({
        'status': 'success',
        'cart_count': total_items
    })

@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        try:
            logger.info("Received webhook request: %s", request.body.decode('utf-8'))
            data = json.loads(request.body)
            message = data.get('message', {})
            
            if message.get('text') == '/check':
                logger.info("Processing /check command")
                handle_check_command(message)
            elif message.get('text') == '/start':
                # Обработка команды /start
                chat_id = message.get('chat', {}).get('id')
                if chat_id:
                    try:
                        requests.post(
                            f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage',
                            json={
                                'chat_id': chat_id,
                                'text': (
                                    "Добро пожаловать в бот уведомлений о заказах!\n\n"
                                    "Для регистрации в системе используйте команду /check\n"
                                    "После регистрации администратор проверит вашу заявку и активирует уведомления."
                                ),
                                'parse_mode': 'HTML'
                            }
                        )
                    except Exception as e:
                        logger.error("Error sending start message: %s", str(e))
            
            return HttpResponse('OK')
        except json.JSONDecodeError as e:
            logger.error("JSON decode error: %s", str(e))
            return HttpResponse('Invalid JSON', status=400)
        except Exception as e:
            logger.error("Error processing webhook: %s", str(e), exc_info=True)
            return HttpResponse('Error', status=500)
    return HttpResponse('Method not allowed', status=405)

def send_telegram_notification(order):
    """Deprecated: Use telegram_bot.send_telegram_notification instead"""
    from .telegram_bot import send_telegram_notification as new_send_notification
    return new_send_notification(order)

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

def create_test_order():
    """Create a test order for testing notifications"""
    # Create a test order
    order = Order.objects.create(
        name="Test User",
        email="test@example.com",
        phone="+79999999999",
        address="Test Address",
        total_amount=1000.00
    )
    
    # Add some test items
    test_product = Product.objects.first()  # Get any product
    if test_product:
        OrderItem.objects.create(
            order=order,
            product=test_product,
            price=test_product.price,
            quantity=2
        )
    
    return order

@csrf_protect
@require_POST
def test_notification(request):
    """Endpoint to test the notification system"""
    try:
        order = create_test_order()
        send_telegram_notification(order)
        return JsonResponse({
            'status': 'success',
            'message': 'Тестовое уведомление отправлено'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_protect
def test_notification_view(request):
    """View to display the test notification page"""
    get_token(request)  # Ensure CSRF token is set
    return render(request, 'cart/test_notification.html')