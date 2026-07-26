from decimal import Decimal

from apps.shop.models import CartItem


class InsufficientStockError(Exception):
    pass


def add_to_cart(cart, product, quantity=1):
    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, defaults={"quantity": quantity}
    )
    if not created:
        item.quantity += quantity
        item.save()
    return item


def remove_from_cart(cart, product):
    CartItem.objects.filter(cart=cart, product=product).delete()


def cart_total(cart):
    return sum(
        (item.subtotal for item in cart.items.select_related("product")), Decimal("0")
    )
