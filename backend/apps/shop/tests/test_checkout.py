from decimal import Decimal

import pytest

from apps.core.factories import UserFactory
from apps.shop.factories import ProductFactory
from apps.shop.models import Cart, Order, OrderItem
from apps.shop.services import InsufficientStockError, add_to_cart, checkout


@pytest.mark.django_db
def test_checkout_creates_order_with_items_and_correct_total():
    cart = Cart.objects.create(user=UserFactory())
    product = ProductFactory(price="10.00", stock=5)
    add_to_cart(cart, product, quantity=2)

    order = checkout(cart)

    assert order.total == Decimal("20.00")
    assert OrderItem.objects.filter(order=order).count() == 1
    item = OrderItem.objects.get(order=order)
    assert item.product == product
    assert item.quantity == 2
    assert item.unit_price == Decimal("10.00")


@pytest.mark.django_db
def test_checkout_decrements_product_stock():
    cart = Cart.objects.create(user=UserFactory())
    product = ProductFactory(stock=5)
    add_to_cart(cart, product, quantity=2)

    checkout(cart)

    product.refresh_from_db()
    assert product.stock == 3


@pytest.mark.django_db
def test_checkout_clears_the_cart():
    cart = Cart.objects.create(user=UserFactory())
    add_to_cart(cart, ProductFactory(), quantity=1)

    checkout(cart)

    assert cart.items.count() == 0


@pytest.mark.django_db
def test_checkout_raises_on_empty_cart():
    cart = Cart.objects.create(user=UserFactory())

    with pytest.raises(ValueError):
        checkout(cart)


@pytest.mark.django_db
def test_checkout_rolls_back_on_insufficient_stock():
    cart = Cart.objects.create(user=UserFactory())
    in_stock = ProductFactory(stock=5)
    out_of_stock = ProductFactory(stock=1)
    add_to_cart(cart, in_stock, quantity=2)
    add_to_cart(cart, out_of_stock, quantity=2)

    with pytest.raises(InsufficientStockError):
        checkout(cart)

    assert Order.objects.count() == 0
    in_stock.refresh_from_db()
    assert in_stock.stock == 5
    assert cart.items.count() == 2
