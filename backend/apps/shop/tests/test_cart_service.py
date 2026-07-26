from decimal import Decimal

import pytest

from apps.core.factories import UserFactory
from apps.shop.factories import ProductFactory
from apps.shop.models import Cart, CartItem
from apps.shop.services import add_to_cart, cart_total, remove_from_cart


@pytest.mark.django_db
def test_add_to_cart_creates_item():
    cart = Cart.objects.create(user=UserFactory())
    product = ProductFactory(price="10.00")

    item = add_to_cart(cart, product, quantity=2)

    assert item.quantity == 2
    assert CartItem.objects.filter(cart=cart, product=product).count() == 1


@pytest.mark.django_db
def test_add_to_cart_increments_existing_item():
    cart = Cart.objects.create(user=UserFactory())
    product = ProductFactory()

    add_to_cart(cart, product, quantity=1)
    item = add_to_cart(cart, product, quantity=2)

    assert item.quantity == 3
    assert CartItem.objects.filter(cart=cart, product=product).count() == 1


@pytest.mark.django_db
def test_remove_from_cart_deletes_item():
    cart = Cart.objects.create(user=UserFactory())
    product = ProductFactory()
    add_to_cart(cart, product, quantity=1)

    remove_from_cart(cart, product)

    assert CartItem.objects.filter(cart=cart, product=product).count() == 0


@pytest.mark.django_db
def test_cart_total_sums_subtotals():
    cart = Cart.objects.create(user=UserFactory())
    add_to_cart(cart, ProductFactory(price="10.00"), quantity=2)
    add_to_cart(cart, ProductFactory(price="5.50"), quantity=1)

    assert cart_total(cart) == Decimal("25.50")
