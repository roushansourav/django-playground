import pytest

from apps.shop.factories import ProductFactory


@pytest.mark.django_db
def test_product_factory_creates_valid_product():
    product = ProductFactory()
    assert product.pk is not None
    assert product.active is True
    assert product.category.pk is not None
