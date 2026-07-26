import logging

import pytest

from apps.core.factories import UserFactory
from apps.shop.factories import ProductFactory
from apps.shop.models import Cart
from apps.shop.services import add_to_cart, checkout


@pytest.mark.django_db
def test_order_creation_logs_confirmation(caplog):
    cart = Cart.objects.create(user=UserFactory(email="buyer@example.com"))
    add_to_cart(cart, ProductFactory(), quantity=1)

    with caplog.at_level(logging.INFO, logger="apps.shop.signals"):
        order = checkout(cart)

    assert any(
        f"Order confirmation email queued for order #{order.pk}" in record.message
        for record in caplog.records
    )
    assert any("buyer@example.com" in record.message for record in caplog.records)
