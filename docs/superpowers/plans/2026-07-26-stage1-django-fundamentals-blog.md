# Stage 1: Django Fundamentals — Blog CRUD Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the Django project (`config`), a custom User model (`apps.core`), and a
full CRUD Blog app (`apps.blog`) with server-rendered templates — no auth restrictions yet
(auth arrives in Stage 2).

**Architecture:** One Django project at `backend/`, apps under `backend/apps/`. SQLite
database. Server-rendered templates only (DRF and React arrive in Stage 3). Class-based
views throughout, since Stage 0's mixin exercise was explicitly practice for this.

**Tech Stack:** Python 3.12, Django 5.2 LTS, SQLite, Django's built-in `TestCase`
(pytest-django is introduced in Stage 2, not used here).

## Global Constraints

- Python: 3.12 (backend/.venv, already provisioned).
- Django: `>=5.2,<5.3` (5.2 LTS).
- Database: SQLite (`backend/db.sqlite3`), per spec — no Postgres yet.
- `AUTH_USER_MODEL` must point at a custom user model from the start (`core.User`) — Django
  cannot swap the user model after the first migration without a painful reset, so it goes
  in now even though login/auth views arrive in Stage 2.
- No authentication/permission restrictions on Blog views in this stage — every view is
  publicly accessible. Stage 2 adds auth.
- Every task ends with something runnable: `manage.py runserver` serving working pages, or
  `manage.py test` passing.

---

### Task 1: Bootstrap Django project

**Files:**
- Modify: `backend/requirements-dev.txt`
- Create: `backend/manage.py`
- Create: `backend/config/__init__.py`
- Create: `backend/config/settings.py`
- Create: `backend/config/urls.py`
- Create: `backend/config/wsgi.py`
- Create: `backend/config/asgi.py`

**Interfaces:**
- Produces: a runnable Django project. `INSTALLED_APPS`, `ROOT_URLCONF = "config.urls"`,
  `DATABASES` (SQLite at `BASE_DIR / "db.sqlite3"`) — later tasks add to `INSTALLED_APPS`
  and `config/urls.py`.

- [ ] **Step 1: Install Django and refreeze requirements**

```bash
cd ~/django-playground/backend
.venv/bin/pip install "Django>=5.2,<5.3"
.venv/bin/pip freeze > requirements-dev.txt
```

- [ ] **Step 2: Scaffold the project**

```bash
cd ~/django-playground/backend
.venv/bin/django-admin startproject config .
```

This creates `manage.py`, `config/__init__.py`, `config/settings.py`, `config/urls.py`,
`config/wsgi.py`, `config/asgi.py` with Django's defaults.

- [ ] **Step 3: Point settings at SQLite explicitly and confirm BASE_DIR**

Open `backend/config/settings.py`. Confirm (Django's `startproject` already generates this,
so this step is verification, not a rewrite) it contains:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

- [ ] **Step 4: Run the dev server to confirm it boots**

Run: `cd ~/django-playground/backend && .venv/bin/python manage.py runserver 8000 &`
then `curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/`
Expected: `200` (Django's default welcome page). Stop the server afterward:
`kill %1` (or `pkill -f "manage.py runserver"`).

- [ ] **Step 5: Commit**

```bash
cd ~/django-playground
git add backend/requirements-dev.txt backend/manage.py backend/config/
git commit -m "Bootstrap Django project (config)"
```

---

### Task 2: Custom User model (`apps.core`)

**Files:**
- Create: `backend/apps/__init__.py`
- Create: `backend/apps/core/__init__.py`
- Create: `backend/apps/core/apps.py`
- Create: `backend/apps/core/models.py`
- Modify: `backend/config/settings.py` (add `apps.core` to `INSTALLED_APPS`, add
  `AUTH_USER_MODEL`, add `apps` to `sys.path` handling via `BASE_DIR / "apps"` on
  `INSTALLED_APPS` naming — see Step 2)
- Test: `backend/apps/core/tests.py`

**Interfaces:**
- Produces: `apps.core.models.User`, a subclass of `django.contrib.auth.models.AbstractUser`
  with no extra fields yet. Later tasks' `Post.author` field is a `ForeignKey` to
  `settings.AUTH_USER_MODEL`, never importing `User` directly.

- [ ] **Step 1: Create the apps package**

```bash
mkdir -p ~/django-playground/backend/apps/core
touch ~/django-playground/backend/apps/__init__.py
touch ~/django-playground/backend/apps/core/__init__.py
```

- [ ] **Step 2: Write `backend/apps/core/apps.py`**

```python
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
```

- [ ] **Step 3: Write `backend/apps/core/models.py`**

```python
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model. No extra fields yet — exists so AUTH_USER_MODEL
    can point here from project creation, avoiding an unswappable default."""
```

- [ ] **Step 4: Update `backend/config/settings.py`**

`manage.py` (generated in Task 1) already adds `backend/` — the directory containing
`manage.py` — to `sys.path`, and `backend/apps/__init__.py` (Step 1) makes `apps` a
regular package. So `apps.core` and later `apps.blog` import cleanly as dotted packages
with no extra `sys.path` changes needed.

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.core",
]
```

Add anywhere below `INSTALLED_APPS`:

```python
AUTH_USER_MODEL = "core.User"
```

- [ ] **Step 5: Write the failing test**

```python
# backend/apps/core/tests.py
from django.contrib.auth import get_user_model
from django.test import TestCase


class UserModelTests(TestCase):
    def test_auth_user_model_is_core_user(self):
        User = get_user_model()
        self.assertEqual(User.__name__, "User")
        self.assertEqual(User._meta.app_label, "core")

    def test_can_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(username="alice", password="testpass123")
        self.assertTrue(user.check_password("testpass123"))
```

- [ ] **Step 6: Run test to verify it fails**

Run: `cd ~/django-playground/backend && .venv/bin/python manage.py test apps.core -v 2`
Expected: FAIL — no migrations exist yet for `core`, so the test database can't create the
`auth_user`/`core_user` table (`django.db.utils.OperationalError` or a migration-related
error).

- [ ] **Step 7: Make migrations and migrate**

```bash
cd ~/django-playground/backend
.venv/bin/python manage.py makemigrations core
.venv/bin/python manage.py migrate
```

- [ ] **Step 8: Run test to verify it passes**

Run: `cd ~/django-playground/backend && .venv/bin/python manage.py test apps.core -v 2`
Expected: both tests PASS.

- [ ] **Step 9: Commit**

```bash
cd ~/django-playground
git add backend/apps/__init__.py backend/apps/core/ backend/config/settings.py
git commit -m "Add custom User model (apps.core)"
```

---

### Task 3: Blog Post model (`apps.blog`)

**Files:**
- Create: `backend/apps/blog/__init__.py`
- Create: `backend/apps/blog/apps.py`
- Create: `backend/apps/blog/models.py`
- Modify: `backend/config/settings.py` (add `apps.blog` to `INSTALLED_APPS`)
- Test: `backend/apps/blog/tests/__init__.py`
- Test: `backend/apps/blog/tests/test_models.py`

**Interfaces:**
- Produces: `apps.blog.models.Post` with fields `title: CharField(max_length=200)`,
  `slug: SlugField(unique=True)`, `body: TextField()`,
  `author: ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name="posts")`,
  `published: BooleanField(default=False)`, `created_at: DateTimeField(auto_now_add=True)`,
  `updated_at: DateTimeField(auto_now=True)`. `Post.__str__` returns `self.title`.
  `Post._meta.ordering = ["-created_at"]`.

- [ ] **Step 1: Create the app package**

```bash
mkdir -p ~/django-playground/backend/apps/blog/tests
touch ~/django-playground/backend/apps/blog/__init__.py
touch ~/django-playground/backend/apps/blog/tests/__init__.py
```

- [ ] **Step 2: Write `backend/apps/blog/apps.py`**

```python
from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.blog"
```

- [ ] **Step 3: Write the failing test**

```python
# backend/apps/blog/tests/test_models.py
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.blog.models import Post


class PostModelTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(username="alice", password="testpass123")

    def test_str_returns_title(self):
        post = Post.objects.create(
            title="Hello World",
            slug="hello-world",
            body="First post.",
            author=self.author,
        )
        self.assertEqual(str(post), "Hello World")

    def test_defaults(self):
        post = Post.objects.create(
            title="Draft", slug="draft", body="...", author=self.author
        )
        self.assertFalse(post.published)
        self.assertIsNotNone(post.created_at)
        self.assertIsNotNone(post.updated_at)

    def test_ordered_newest_first(self):
        older = Post.objects.create(
            title="Older", slug="older", body="...", author=self.author
        )
        newer = Post.objects.create(
            title="Newer", slug="newer", body="...", author=self.author
        )
        self.assertEqual(list(Post.objects.all()), [newer, older])

    def test_slug_must_be_unique(self):
        Post.objects.create(
            title="One", slug="same-slug", body="...", author=self.author
        )
        with self.assertRaises(Exception):
            Post.objects.create(
                title="Two", slug="same-slug", body="...", author=self.author
            )
```

- [ ] **Step 4: Write `backend/apps/blog/models.py`**

```python
from django.conf import settings
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
```

- [ ] **Step 5: Add `apps.blog` to `INSTALLED_APPS`** in `backend/config/settings.py`,
  after `"apps.core"`.

- [ ] **Step 6: Run test to verify it fails, then make/run migrations**

Run: `cd ~/django-playground/backend && .venv/bin/python manage.py test apps.blog -v 2`
Expected: FAILs (no migration yet for `blog` — table doesn't exist).

```bash
cd ~/django-playground/backend
.venv/bin/python manage.py makemigrations blog
.venv/bin/python manage.py migrate
```

- [ ] **Step 7: Run test to verify it passes**

Run: `cd ~/django-playground/backend && .venv/bin/python manage.py test apps.blog -v 2`
Expected: all 4 tests PASS.

- [ ] **Step 8: Commit**

```bash
cd ~/django-playground
git add backend/apps/blog/ backend/config/settings.py
git commit -m "Add Post model (apps.blog)"
```

---

### Task 4: Django admin for Post

**Files:**
- Create: `backend/apps/blog/admin.py`
- Test: `backend/apps/blog/tests/test_admin.py`

**Interfaces:**
- Produces: `Post` registered in Django admin with `list_display = ("title", "author",
  "published", "created_at")` and `prepopulated_fields = {"slug": ("title",)}`.
- Consumes: `Post` from `apps.blog.models` (Task 3), `get_user_model()` for the superuser
  used in tests.

- [ ] **Step 1: Write the failing test**

```python
# backend/apps/blog/tests/test_admin.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import Post


class PostAdminTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.superuser = User.objects.create_superuser(
            username="admin", password="testpass123", email="admin@example.com"
        )
        self.client.force_login(self.superuser)
        self.post = Post.objects.create(
            title="Hello", slug="hello", body="...", author=self.superuser
        )

    def test_post_changelist_loads(self):
        url = reverse("admin:blog_post_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello")

    def test_post_change_page_loads(self):
        url = reverse("admin:blog_post_change", args=[self.post.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ~/django-playground/backend && .venv/bin/python manage.py test apps.blog.tests.test_admin -v 2`
Expected: FAIL — `NoReverseMatch` (`Post` isn't registered, so `admin:blog_post_changelist`
doesn't exist).

- [ ] **Step 3: Write `backend/apps/blog/admin.py`**

```python
from django.contrib import admin

from apps.blog.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published", "created_at")
    prepopulated_fields = {"slug": ("title",)}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd ~/django-playground/backend && .venv/bin/python manage.py test apps.blog.tests.test_admin -v 2`
Expected: both tests PASS.

- [ ] **Step 5: Commit**

```bash
cd ~/django-playground
git add backend/apps/blog/admin.py backend/apps/blog/tests/test_admin.py
git commit -m "Register Post in Django admin"
```

---

### Task 5: Blog list & detail views

**Files:**
- Create: `backend/apps/blog/urls.py`
- Create: `backend/apps/blog/views.py`
- Create: `backend/templates/blog/post_list.html`
- Create: `backend/templates/blog/post_detail.html`
- Create: `backend/templates/base.html`
- Modify: `backend/config/urls.py` (include blog urls)
- Modify: `backend/config/settings.py` (add `BASE_DIR / "templates"` to `TEMPLATES[0]["DIRS"]`)
- Test: `backend/apps/blog/tests/test_views.py`

**Interfaces:**
- Produces: `PostListView` (ListView, `template_name="blog/post_list.html"`,
  `context_object_name="posts"`, queryset filtered to `published=True`), `PostDetailView`
  (DetailView, `template_name="blog/post_detail.html"`, `context_object_name="post"`,
  looked up by `slug` via `slug_url_kwarg="slug"`). URL names: `"blog:post_list"` at `""`,
  `"blog:post_detail"` at `"<slug:slug>/"`, `app_name = "blog"`.

- [ ] **Step 1: Write the failing tests**

```python
# backend/apps/blog/tests/test_views.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import Post


class PostListViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(username="alice", password="testpass123")
        self.published = Post.objects.create(
            title="Published Post",
            slug="published-post",
            body="...",
            author=self.author,
            published=True,
        )
        self.draft = Post.objects.create(
            title="Draft Post", slug="draft-post", body="...", author=self.author
        )

    def test_list_shows_only_published(self):
        response = self.client.get(reverse("blog:post_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Published Post")
        self.assertNotContains(response, "Draft Post")


class PostDetailViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(username="alice", password="testpass123")
        self.post = Post.objects.create(
            title="Hello World",
            slug="hello-world",
            body="Full body text.",
            author=self.author,
            published=True,
        )

    def test_detail_shows_title_and_body(self):
        url = reverse("blog:post_detail", kwargs={"slug": "hello-world"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello World")
        self.assertContains(response, "Full body text.")

    def test_detail_404_for_unknown_slug(self):
        url = reverse("blog:post_detail", kwargs={"slug": "does-not-exist"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/django-playground/backend && .venv/bin/python manage.py test apps.blog.tests.test_views -v 2`
Expected: FAIL — `NoReverseMatch` (`blog` urls don't exist yet).

- [ ] **Step 3: Write `backend/templates/base.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Django Playground{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

- [ ] **Step 4: Write `backend/templates/blog/post_list.html`**

```html
{% extends "base.html" %}

{% block title %}Blog{% endblock %}

{% block content %}
<h1>Blog</h1>
<ul>
    {% for post in posts %}
    <li><a href="{% url 'blog:post_detail' post.slug %}">{{ post.title }}</a></li>
    {% endfor %}
</ul>
{% endblock %}
```

- [ ] **Step 5: Write `backend/templates/blog/post_detail.html`**

```html
{% extends "base.html" %}

{% block title %}{{ post.title }}{% endblock %}

{% block content %}
<h1>{{ post.title }}</h1>
<p>{{ post.body }}</p>
{% endblock %}
```

- [ ] **Step 6: Write `backend/apps/blog/views.py`**

```python
from django.views.generic import DetailView, ListView

from apps.blog.models import Post


class PostListView(ListView):
    template_name = "blog/post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        return Post.objects.filter(published=True)


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"
    slug_url_kwarg = "slug"
```

- [ ] **Step 7: Write `backend/apps/blog/urls.py`**

```python
from django.urls import path

from apps.blog import views

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
]
```

- [ ] **Step 8: Update `backend/config/urls.py`**

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("blog/", include("apps.blog.urls")),
]
```

- [ ] **Step 9: Update `TEMPLATES` in `backend/config/settings.py`**

In the `TEMPLATES` list's single dict, change:

```python
"DIRS": [],
```

to:

```python
"DIRS": [BASE_DIR / "templates"],
```

- [ ] **Step 10: Run tests to verify they pass**

Run: `cd ~/django-playground/backend && .venv/bin/python manage.py test apps.blog.tests.test_views -v 2`
Expected: all 3 tests PASS.

- [ ] **Step 11: Commit**

```bash
cd ~/django-playground
git add backend/apps/blog/urls.py backend/apps/blog/views.py backend/apps/blog/tests/test_views.py \
  backend/templates/ backend/config/urls.py backend/config/settings.py
git commit -m "Add Blog list and detail views"
```

---

### Task 6: Blog CRUD (create, update, delete)

**Files:**
- Modify: `backend/apps/blog/views.py`
- Modify: `backend/apps/blog/urls.py`
- Create: `backend/templates/blog/post_form.html`
- Create: `backend/templates/blog/post_confirm_delete.html`
- Test: `backend/apps/blog/tests/test_crud_views.py`

**Interfaces:**
- Produces: `PostCreateView` (CreateView, `fields = ["title", "slug", "body",
  "published"]`, `template_name="blog/post_form.html"`, on success redirects to
  `post.get_absolute_url()`), `PostUpdateView` (UpdateView, same fields/template),
  `PostDeleteView` (DeleteView, `template_name="blog/post_confirm_delete.html"`,
  `success_url = reverse_lazy("blog:post_list")`). All three set `self.object.author =
  self.request.user` is NOT applicable here (no auth yet) — instead
  `PostCreateView.form_valid` must assign an author, so it hardcodes the first user via
  `get_user_model().objects.first()` for this stage only (a comment must say Stage 2
  replaces this with `self.request.user`). Adds `Post.get_absolute_url()` returning
  `reverse("blog:post_detail", kwargs={"slug": self.slug})`. URL names: `"blog:post_create"`
  at `"new/"`, `"blog:post_update"` at `"<slug:slug>/edit/"`, `"blog:post_delete"` at
  `"<slug:slug>/delete/"`.

- [ ] **Step 1: Write the failing tests**

```python
# backend/apps/blog/tests/test_crud_views.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import Post


class PostCreateViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(username="alice", password="testpass123")

    def test_get_form_renders(self):
        response = self.client.get(reverse("blog:post_create"))
        self.assertEqual(response.status_code, 200)

    def test_post_creates_post_with_author(self):
        response = self.client.post(
            reverse("blog:post_create"),
            {
                "title": "New Post",
                "slug": "new-post",
                "body": "Body text.",
                "published": True,
            },
        )
        post = Post.objects.get(slug="new-post")
        self.assertEqual(post.title, "New Post")
        self.assertEqual(post.author, self.author)
        self.assertRedirects(response, reverse("blog:post_detail", kwargs={"slug": "new-post"}))


class PostUpdateViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(username="alice", password="testpass123")
        self.post = Post.objects.create(
            title="Original", slug="original", body="...", author=self.author
        )

    def test_post_updates_title(self):
        response = self.client.post(
            reverse("blog:post_update", kwargs={"slug": "original"}),
            {
                "title": "Updated Title",
                "slug": "original",
                "body": "...",
                "published": False,
            },
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Title")
        self.assertRedirects(response, reverse("blog:post_detail", kwargs={"slug": "original"}))


class PostDeleteViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(username="alice", password="testpass123")
        self.post = Post.objects.create(
            title="To Delete", slug="to-delete", body="...", author=self.author
        )

    def test_post_deletes(self):
        response = self.client.post(
            reverse("blog:post_delete", kwargs={"slug": "to-delete"})
        )
        self.assertFalse(Post.objects.filter(slug="to-delete").exists())
        self.assertRedirects(response, reverse("blog:post_list"))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/django-playground/backend && .venv/bin/python manage.py test apps.blog.tests.test_crud_views -v 2`
Expected: FAIL — `NoReverseMatch` (create/update/delete urls don't exist yet).

- [ ] **Step 3: Add `get_absolute_url` to `Post`** in `backend/apps/blog/models.py` — insert
  after the `__str__` method:

```python
    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("blog:post_detail", kwargs={"slug": self.slug})
```

- [ ] **Step 4: Write `backend/templates/blog/post_form.html`**

```html
{% extends "base.html" %}

{% block title %}{% if post %}Edit Post{% else %}New Post{% endif %}{% endblock %}

{% block content %}
<h1>{% if post %}Edit Post{% else %}New Post{% endif %}</h1>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Save</button>
</form>
{% endblock %}
```

- [ ] **Step 5: Write `backend/templates/blog/post_confirm_delete.html`**

```html
{% extends "base.html" %}

{% block title %}Delete Post{% endblock %}

{% block content %}
<h1>Delete "{{ post.title }}"?</h1>
<form method="post">
    {% csrf_token %}
    <button type="submit">Confirm delete</button>
</form>
{% endblock %}
```

- [ ] **Step 6: Add CRUD views to `backend/apps/blog/views.py`**

Add these imports at the top (alongside the existing `DetailView, ListView` import, extend
it to include `CreateView, DeleteView, UpdateView`):

```python
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
```

Append to the file:

```python
class PostCreateView(CreateView):
    model = Post
    fields = ["title", "slug", "body", "published"]
    template_name = "blog/post_form.html"

    def form_valid(self, form):
        # Stage 2 replaces this with self.request.user once auth exists.
        form.instance.author = get_user_model().objects.first()
        return super().form_valid(form)


class PostUpdateView(UpdateView):
    model = Post
    fields = ["title", "slug", "body", "published"]
    template_name = "blog/post_form.html"


class PostDeleteView(DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("blog:post_list")
```

- [ ] **Step 7: Update `backend/apps/blog/urls.py`**

```python
from django.urls import path

from apps.blog import views

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("new/", views.PostCreateView.as_view(), name="post_create"),
    path("<slug:slug>/edit/", views.PostUpdateView.as_view(), name="post_update"),
    path("<slug:slug>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path("<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
]
```

Note the ordering: `post_create`/`edit`/`delete` patterns must come before the bare
`<slug:slug>/` detail pattern, since `"new/"` would otherwise be captured by
`<slug:slug>/` (Django matches patterns top-to-bottom).

- [ ] **Step 8: Run tests to verify they pass**

Run: `cd ~/django-playground/backend && .venv/bin/python manage.py test apps.blog -v 2`
Expected: all tests across the whole `blog` app PASS (this task's 5 plus Tasks 3-5's
tests, since they all share the `Post` model and URLconf).

- [ ] **Step 9: Commit**

```bash
cd ~/django-playground
git add backend/apps/blog/models.py backend/apps/blog/views.py backend/apps/blog/urls.py \
  backend/apps/blog/tests/test_crud_views.py backend/templates/blog/post_form.html \
  backend/templates/blog/post_confirm_delete.html
git commit -m "Add Blog CRUD (create, update, delete) views"
```

---

## After this plan

Run the full test suite (`manage.py test`) and `runserver` to confirm the whole Blog CRUD
flow works end to end in a browser. Then walk through Stage 2 (forms/auth/class-based views
depth, pytest-django) with the learner: the hardcoded `get_user_model().objects.first()` in
`PostCreateView.form_valid` (Task 6) is the first thing Stage 2 removes in favor of real
auth. Stage 2 gets its own plan once this one is done.
