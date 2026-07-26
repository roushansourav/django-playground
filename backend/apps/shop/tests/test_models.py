import pytest
from django.db import IntegrityError

from apps.shop.models import Category, Product


@pytest.mark.django_db
def test_category_str_returns_name():
    category = Category.objects.create(name="Books", slug="books")
    assert str(category) == "Books"


@pytest.mark.django_db
def test_category_name_must_be_unique():
    Category.objects.create(name="Books", slug="books")
    with pytest.raises(IntegrityError):
        Category.objects.create(name="Books", slug="books-2")


@pytest.mark.django_db
def test_product_str_returns_name():
    category = Category.objects.create(name="Books", slug="books")
    product = Product.objects.create(
        name="Clean Code", slug="clean-code", price="29.99", stock=10, category=category
    )
    assert str(product) == "Clean Code"
    assert product.active is True
