def cart_total_items(request):
    cart = request.session.get('cart', {})
    total_items = sum(int(qty) for qty in cart.values() if int(qty) > 0)
    return {'cart_total_items': total_items} 