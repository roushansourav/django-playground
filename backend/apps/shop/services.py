from decimal import Decimal

from django.db import transaction

from apps.shop.models import CartItem, Order, OrderItem


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


@transaction.atomic
def checkout(cart):
    items = list(cart.items.select_related("product"))
    if not items:
        raise ValueError("Cart is empty")

    for item in items:
        if item.quantity > item.product.stock:
            raise InsufficientStockError(f"Not enough stock for {item.product.name}")

    order = Order.objects.create(user=cart.user, total=Decimal("0"))
    total = Decimal("0")
    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            unit_price=item.product.price,
        )
        item.product.stock -= item.quantity
        item.product.save()
        total += item.subtotal

    order.total = total
    order.save()
    cart.items.all().delete()
    return order
