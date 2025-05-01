def cart_processor(request):
    cart = request.session.get('cart', {})
    total_items = sum(int(quantity) for quantity in cart.values())
    return {
        'cart_total_items': total_items
    } 