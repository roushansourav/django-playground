# Stage 4a: Shop Models, Cart Service, Checkout, Signal Implementation Plan

**Goal:** Build the shop app's domain layer — Category/Product/Cart/CartItem/Order/OrderItem
models, a cart service, a transactional checkout service, and a post-save signal stub for
order confirmation (the seam Stage 4b's Celery task will hang off of).

**Architecture:** New `apps.shop` Django app, models-only + service-layer functions
(`apps/shop/services.py`), no views/API yet (that's Stage 4c) and no React (Stage 4d).
Tested entirely through pytest-django + factory_boy, following the `apps.blog` app's
conventions (factories.py at app root, tests/ package).

**Tech Stack:** Django 5.2, pytest-django, factory_boy — all already installed.

## Global Constraints

- SQLite only (project-wide). Do not use `select_for_update()` — SQLite silently no-ops it,
  and the checkout logic must not rely on it. `transaction.atomic()` is sufficient here.
- Money fields: `DecimalField(max_digits=10, decimal_places=2)` everywhere prices are stored.
- Follow `apps.blog`'s file layout: `models.py`, `admin.py`, `factories.py` (app root),
  `tests/` package with `test_models.py`, `test_factories.py`, etc.
- `AUTH_USER_MODEL` is `core.User` (see `apps.core.models`). Use `settings.AUTH_USER_MODEL`
  in FK/O2O fields, never import the User model directly.

---

### Task 1: Shop app scaffold + Category/Product models + admin + factories

**Files:**
- Create: `backend/apps/shop/__init__.py`, `apps.py`, `models.py`, `admin.py`, `factories.py`
- Create: `backend/apps/shop/migrations/__init__.py` (via `makemigrations`)
- Create: `backend/apps/shop/tests/__init__.py`, `test_models.py`, `test_factories.py`
- Modify: `backend/config/settings.py` (add `'apps.shop'` to `INSTALLED_APPS`, after `'apps.blog'`)

**Interfaces:**
- Produces: `Category(name, slug)`, `Product(name, slug, description, price, stock, category, active)`.
  `ProductFactory`, `CategoryFactory` for later tasks to import.

- [ ] **Step 1: Scaffold the app**

```bash
cd ~/django-playground/backend
.venv/bin/python manage.py startapp shop apps/shop
mkdir -p apps/shop/tests
touch apps/shop/tests/__init__.py
rm apps/shop/tests.py apps/shop/views.py  # startapp scaffolds these; app has neither yet
```

- [ ] **Step 2: Write `apps/shop/apps.py`**

```python
from django.apps import AppConfig


class ShopConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.shop"
```

- [ ] **Step 3: Add to `INSTALLED_APPS`** in `backend/config/settings.py`, immediately after `'apps.blog'`:

```python
    'apps.shop',
```

- [ ] **Step 4: Write the failing test**

```python
# backend/apps/shop/tests/test_models.py
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
```

- [ ] **Step 5: Run test to verify it fails**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/shop/tests/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'apps.shop.models'` (models.py still scaffold-empty) or `ImportError: cannot import name 'Category'`.

- [ ] **Step 6: Write `apps/shop/models.py`**

```python
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
```

- [ ] **Step 7: Make migrations and run tests**

```bash
cd ~/django-playground/backend
.venv/bin/python manage.py makemigrations shop
.venv/bin/python -m pytest apps/shop/tests/test_models.py -v
```

Expected: PASS (3 tests).

- [ ] **Step 8: Write `apps/shop/admin.py`**

```python
from django.contrib import admin

from apps.shop.models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "active")
    list_filter = ("category", "active")
    prepopulated_fields = {"slug": ("name",)}
```

- [ ] **Step 9: Write `apps/shop/factories.py`**

```python
import factory

from apps.shop.models import Category, Product


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"Product {n}")
    slug = factory.Sequence(lambda n: f"product-{n}")
    description = factory.Faker("paragraph")
    price = "19.99"
    stock = 10
    category = factory.SubFactory(CategoryFactory)
```

- [ ] **Step 10: Write the failing-then-passing factory test**

```python
# backend/apps/shop/tests/test_factories.py
import pytest

from apps.shop.factories import ProductFactory


@pytest.mark.django_db
def test_product_factory_creates_valid_product():
    product = ProductFactory()
    assert product.pk is not None
    assert product.active is True
    assert product.category.pk is not None
```

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/shop/tests/ -v`
Expected: PASS (4 tests total).

- [ ] **Step 11: Commit**

```bash
cd ~/django-playground
git add backend/apps/shop/ backend/config/settings.py
git commit -m "Add shop app with Category and Product models"
```

---

### Task 2: Cart/CartItem models + cart service

**Files:**
- Modify: `backend/apps/shop/models.py`, `admin.py`, `factories.py`
- Create: `backend/apps/shop/services.py`
- Create: `backend/apps/shop/tests/test_cart_service.py`

**Interfaces:**
- Consumes: `Product` (Task 1).
- Produces: `Cart(user)`, `CartItem(cart, product, quantity)` with `.subtotal` property.
  `add_to_cart(cart, product, quantity=1) -> CartItem`, `remove_from_cart(cart, product) -> None`,
  `cart_total(cart) -> Decimal`. Later tasks (checkout) consume these.

- [ ] **Step 1: Write the failing test**

```python
# backend/apps/shop/tests/test_cart_service.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/shop/tests/test_cart_service.py -v`
Expected: FAIL — `ImportError: cannot import name 'Cart' from 'apps.shop.models'`.

- [ ] **Step 3: Add `Cart` and `CartItem` to `apps/shop/models.py`**

```python
from django.conf import settings
from django.db import models


# ... Category, Product unchanged above ...


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.quantity} x {self.product}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity
```

(Add `from django.conf import settings` to the existing import line at the top of the file
rather than duplicating the `django.db import models` line.)

- [ ] **Step 4: Write `apps/shop/services.py`**

```python
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
```

- [ ] **Step 5: Make migrations and run tests**

```bash
cd ~/django-playground/backend
.venv/bin/python manage.py makemigrations shop
.venv/bin/python -m pytest apps/shop/tests/test_cart_service.py -v
```

Expected: PASS (4 tests).

- [ ] **Step 6: Register Cart/CartItem as inline admin** — append to `apps/shop/admin.py`:

```python
from apps.shop.models import Cart, CartItem  # extend existing import line


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    inlines = [CartItemInline]
```

- [ ] **Step 7: Add `CartFactory` to `apps/shop/factories.py`**

```python
from apps.core.factories import UserFactory
from apps.shop.models import Cart  # extend existing import line


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    user = factory.SubFactory(UserFactory)
```

- [ ] **Step 8: Full shop regression**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/shop/ -v`
Expected: PASS (8 tests).

- [ ] **Step 9: Commit**

```bash
cd ~/django-playground
git add backend/apps/shop/
git commit -m "Add Cart/CartItem models and cart service"
```

---

### Task 3: Order/OrderItem models + transactional checkout service

**Files:**
- Modify: `backend/apps/shop/models.py`, `admin.py`, `services.py`
- Create: `backend/apps/shop/tests/test_checkout.py`

**Interfaces:**
- Consumes: `Cart`, `CartItem`, `InsufficientStockError` (Task 2).
- Produces: `Order(user, status, total, created_at)`, `OrderItem(order, product, quantity, unit_price)`
  with `.subtotal` property. `checkout(cart) -> Order`, raising `InsufficientStockError` (no partial
  writes) or `ValueError` on an empty cart.

- [ ] **Step 1: Write the failing test**

```python
# backend/apps/shop/tests/test_checkout.py
from decimal import Decimal

import pytest

from apps.core.factories import UserFactory
from apps.shop.factories import ProductFactory
from apps.shop.models import Cart, Order, OrderItem, Product
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
    assert in_stock.stock == 5  # unchanged — no partial write
    assert cart.items.count() == 2  # cart untouched
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/shop/tests/test_checkout.py -v`
Expected: FAIL — `ImportError: cannot import name 'Order' from 'apps.shop.models'`.

- [ ] **Step 3: Add `Order` and `OrderItem` to `apps/shop/models.py`**

```python
class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CONFIRMED)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} ({self.user})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product} @ {self.unit_price}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
```

- [ ] **Step 4: Add `checkout()` to `apps/shop/services.py`**

```python
from decimal import Decimal

from django.db import transaction

from apps.shop.models import CartItem, Order, OrderItem


class InsufficientStockError(Exception):
    pass


# ... add_to_cart, remove_from_cart, cart_total unchanged above ...


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
```

`@transaction.atomic` guarantees the insufficient-stock test's rollback assertions:
raising after `Order.objects.create()` inside the loop would otherwise leave a partial
order. Note the stock check happens in a first pass over all items *before* any write,
so `checkout` never writes anything if any single item is short on stock.

- [ ] **Step 5: Make migrations and run tests**

```bash
cd ~/django-playground/backend
.venv/bin/python manage.py makemigrations shop
.venv/bin/python -m pytest apps/shop/tests/test_checkout.py -v
```

Expected: PASS (5 tests).

- [ ] **Step 6: Register Order/OrderItem in admin** — append to `apps/shop/admin.py`:

```python
from apps.shop.models import Order, OrderItem  # extend existing import line


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total", "created_at")
    list_filter = ("status",)
    inlines = [OrderItemInline]
```

- [ ] **Step 7: Full shop regression**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/shop/ -v`
Expected: PASS (13 tests).

- [ ] **Step 8: Commit**

```bash
cd ~/django-playground
git add backend/apps/shop/
git commit -m "Add Order/OrderItem models and transactional checkout service"
```

---

### Task 4: Order confirmation signal

**Files:**
- Create: `backend/apps/shop/signals.py`
- Modify: `backend/apps/shop/apps.py`
- Create: `backend/apps/shop/tests/test_signals.py`

**Interfaces:**
- Consumes: `Order` (Task 3).
- Produces: a `post_save` receiver that logs an order-confirmation message when an `Order`
  is created. This is the exact seam Stage 4b replaces with `send_order_confirmation.delay(order.id)`
  — keep the log message and logger name (`apps.shop.signals`) stable so that task's plan can
  reference them.

- [ ] **Step 1: Write the failing test**

```python
# backend/apps/shop/tests/test_signals.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/shop/tests/test_signals.py -v`
Expected: FAIL — no log record matches (signal not wired up yet).

- [ ] **Step 3: Write `apps/shop/signals.py`**

```python
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.shop.models import Order

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def send_order_confirmation(sender, instance, created, **kwargs):
    if created:
        logger.info(
            "Order confirmation email queued for order #%s (%s)",
            instance.pk,
            instance.user.email,
        )
```

- [ ] **Step 4: Wire the signal in `apps/shop/apps.py`**

```python
from django.apps import AppConfig


class ShopConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.shop"

    def ready(self):
        import apps.shop.signals  # noqa: F401
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/shop/tests/test_signals.py -v`
Expected: PASS.

- [ ] **Step 6: Full backend regression**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/ -v`
Expected: all pass (38 pre-existing + 14 shop = 52).

- [ ] **Step 7: Commit**

```bash
cd ~/django-playground
git add backend/apps/shop/
git commit -m "Add order confirmation signal on Order creation"
```

---

## After this plan

The shop app has a complete, transaction-safe domain layer: products with stock, a
per-user cart, and checkout that atomically creates an order, decrements stock, and clears
the cart — with a signal firing on order creation. Stage 4b wires that signal's log stub to
a real Celery task (async order confirmation "email"). Stage 4c exposes this layer as a DRF
API. Stage 4d builds the React storefront.
