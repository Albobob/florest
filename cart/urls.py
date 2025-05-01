from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update/', views.update_cart, name='update_cart'),
    path('place-order/', views.place_order, name='place_order'),
    path('webhook/telegram/', views.telegram_webhook, name='telegram_webhook'),
    path('test-notification/', views.test_notification, name='test_notification'),
    path('test-notification-page/', views.test_notification_view, name='test_notification_page'),
]