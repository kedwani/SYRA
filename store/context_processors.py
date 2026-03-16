"""
Context processors for the store app.
"""

from django.contrib.auth.decorators import login_required
from .models import Cart


def cart_item_count(request):
    """
    Add cart item count to all templates.
    """
    cart_items_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items_count = cart.items.count()
        except Cart.DoesNotExist:
            cart_items_count = 0

    return {
        "cart_items_count": cart_items_count,
    }
