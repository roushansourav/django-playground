# Stage 2: Forms, Auth, Comments, Tags Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. (This project has been executing plans directly in-session instead, per an explicit, previously-communicated exception for this solo learning repo — see prior stage execution history.)

**Goal:** Extend the Blog app with real authentication (signup/login/logout, author-only edit/delete), comments, and tags; introduce pytest-django and factory_boy as the project's testing baseline going forward.

**Architecture:** Auth uses Django's built-in `django.contrib.auth` views (login/logout) plus a custom signup view in a new `apps.core.views`. `PostCreateView` drops its Stage-1 hardcoded-author hack in favor of `request.user`; `PostUpdateView`/`PostDeleteView` gain author-only permission checks via `LoginRequiredMixin` + `UserPassesTestMixin`. Comments and Tags are new models on `apps.blog` (Comment FK to Post, Tag M2M to Post), each with their own view/template/test slice.

**Tech Stack:** Django 5.2, pytest-django, factory_boy, Django's class-based views/mixins, Django's built-in auth forms/views.

## Global Constraints

- Database: SQLite (unchanged).
- Testing: from this stage onward, new tests are pytest-style (plain `def test_...` + `assert`), run via `pytest`, not `django.test.TestCase` + `manage.py test`. Existing Stage-1 `TestCase`-based tests keep working unmodified under pytest-django (it can run both).
- `AUTH_USER_MODEL = 'core.User'` (unchanged, already migrated — do not alter this or existing migrations).
- Branch-per-task, PR into `main`, squash-merge, delete branch (established workflow — continue as-is).
- No placeholders: every step below has runnable code.

---

### Task 1: pytest-django + factory_boy bootstrap

**Files:**
- Modify: `backend/requirements-dev.txt`
- Modify: `backend/pytest.ini`
- Create: `backend/apps/core/factories.py`
- Create: `backend/apps/blog/factories.py`
- Test: `backend/apps/blog/tests/test_factories.py`

**Interfaces:**
- Produces: `apps.core.factories.UserFactory` (django_get_or_create not used; plain factory, `Meta.model = get_user_model()`, `username = factory.Sequence(lambda n: f"user{n}")`, password set via `factory.PostGenerationMethodCall("set_password", "testpass123")`). `apps.blog.factories.PostFactory` (`Meta.model = Post`, `title = factory.Faker("sentence")`, `slug = factory.Sequence(lambda n: f"post-{n}")`, `body = factory.Faker("paragraph")`, `author = factory.SubFactory(UserFactory)`, `published = False`). Later tasks' tests may import both.

- [ ] **Step 1: Write the failing test**

```python
# backend/apps/blog/tests/test_factories.py
import pytest

from apps.blog.factories import PostFactory


@pytest.mark.django_db
def test_post_factory_creates_valid_post():
    post = PostFactory()
    assert post.pk is not None
    assert post.published is False
    assert post.author.pk is not None
```

Note: plain pytest functions need `@pytest.mark.django_db` to touch the database — pytest-django blocks DB access by default so tests can't accidentally hit a real database.

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/blog/tests/test_factories.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'apps.blog.factories'` (pytest-django/pytest itself isn't installed yet either, so this will first fail with `ModuleNotFoundError: No module named 'pytest_django'` until Step 3 installs it — that failure is also expected and fine).

- [ ] **Step 3: Install pytest-django and factory_boy, freeze requirements**

```bash
cd ~/django-playground/backend
.venv/bin/pip install pytest-django factory-boy
.venv/bin/pip freeze > requirements-dev.txt
```

- [ ] **Step 4: Update `backend/pytest.ini`**

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
testpaths = tests apps
```

- [ ] **Step 5: Write `backend/apps/core/factories.py`**

```python
import factory

from apps.core.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
```

- [ ] **Step 6: Write `backend/apps/blog/factories.py`**

```python
import factory

from apps.blog.models import Post
from apps.core.factories import UserFactory


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Faker("sentence")
    slug = factory.Sequence(lambda n: f"post-{n}")
    body = factory.Faker("paragraph")
    author = factory.SubFactory(UserFactory)
    published = False
```

- [ ] **Step 7: Run test to verify it passes**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/blog/tests/test_factories.py -v`
Expected: PASS (1 passed).

- [ ] **Step 8: Regression check — confirm pytest can also run existing Stage 1 `TestCase` tests**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/ -v`
Expected: all existing Stage 1 tests (15) plus the new factory test (1) pass — 16 passed.

- [ ] **Step 9: Commit**

```bash
git add backend/requirements-dev.txt backend/pytest.ini backend/apps/core/factories.py backend/apps/blog/factories.py backend/apps/blog/tests/test_factories.py
git commit -m "Add pytest-django and factory_boy"
```

---

### Task 2: Real authentication (signup, login, logout, author-only permissions)

**Files:**
- Create: `backend/apps/core/forms.py`
- Create: `backend/apps/core/views.py`
- Create: `backend/apps/core/urls.py`
- Modify: `backend/apps/core/tests.py`
- Modify: `backend/apps/blog/views.py`
- Modify: `backend/apps/blog/tests/test_crud_views.py`
- Create: `backend/apps/blog/tests/test_permissions.py`
- Modify: `backend/config/urls.py`
- Modify: `backend/config/settings.py`
- Create: `backend/templates/registration/login.html`
- Create: `backend/templates/registration/signup.html`
- Modify: `backend/templates/base.html`

**Interfaces:**
- Consumes: `apps.core.factories.UserFactory`, `apps.blog.factories.PostFactory` (Task 1).
- Produces: `apps.core.forms.SignupForm` (subclasses `UserCreationForm`, `Meta.model = get_user_model()`, `fields = ("username", "email")`). `apps.core.views.SignupView` (CreateView, logs the new user in on success, redirects to `"blog:post_list"`). URL name `"core:signup"` at `/accounts/signup/`. Django's built-in auth URLs mounted at `/accounts/` giving url names `"login"` and `"logout"`. `PostCreateView` now requires login and sets `author = request.user`. `PostUpdateView`/`PostDeleteView` require login AND `post.author == request.user` (403 otherwise).

- [ ] **Step 1: Write the failing tests**

```python
# Append to backend/apps/core/tests.py
from django.urls import reverse


class SignupViewTests(TestCase):
    def test_get_form_renders(self):
        response = self.client.get(reverse("core:signup"))
        self.assertEqual(response.status_code, 200)

    def test_post_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("core:signup"),
            {
                "username": "newuser",
                "password1": "a-very-strong-pass123",
                "password2": "a-very-strong-pass123",
            },
        )
        User = get_user_model()
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertRedirects(response, reverse("blog:post_list"))
        response2 = self.client.get(reverse("blog:post_create"))
        self.assertEqual(response2.status_code, 200)
```

```python
# backend/apps/blog/tests/test_permissions.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import Post


class PostCreatePermissionTests(TestCase):
    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse("blog:post_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)


class PostUpdateDeletePermissionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(username="alice", password="testpass123")
        self.other = User.objects.create_user(username="bob", password="testpass123")
        self.post = Post.objects.create(
            title="Original", slug="original", body="...", author=self.author
        )

    def test_anonymous_redirected_to_login_on_update(self):
        response = self.client.get(reverse("blog:post_update", kwargs={"slug": "original"}))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_non_author_forbidden_on_update(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("blog:post_update", kwargs={"slug": "original"}))
        self.assertEqual(response.status_code, 403)

    def test_author_can_access_update(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse("blog:post_update", kwargs={"slug": "original"}))
        self.assertEqual(response.status_code, 200)

    def test_non_author_forbidden_on_delete(self):
        self.client.force_login(self.other)
        response = self.client.post(reverse("blog:post_delete", kwargs={"slug": "original"}))
        self.assertEqual(response.status_code, 403)
```

Also update the existing `backend/apps/blog/tests/test_crud_views.py` — `PostCreateViewTests`, `PostUpdateViewTests`, and `PostDeleteViewTests` must log in before posting, since these views now require auth:

```python
# In PostCreateViewTests.setUp, add:
        self.client.force_login(self.author)

# In PostUpdateViewTests.setUp, add:
        self.client.force_login(self.author)

# In PostDeleteViewTests.setUp, add:
        self.client.force_login(self.author)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/core/tests.py apps/blog/tests/test_permissions.py apps/blog/tests/test_crud_views.py -v`
Expected: FAIL — `NoReverseMatch` for `"core:signup"`/`"login"`, and the CRUD tests now failing because `PostCreateView` still uses the Stage-1 hardcoded-author hack while the test's `setUp` calls `force_login` without the view yet requiring or using it consistently.

- [ ] **Step 3: Write `backend/apps/core/forms.py`**

```python
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email")
```

- [ ] **Step 4: Write `backend/apps/core/views.py`**

```python
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView

from apps.core.forms import SignupForm


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("blog:post_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response
```

- [ ] **Step 5: Write `backend/apps/core/urls.py`**

```python
from django.urls import path

from apps.core import views

app_name = "core"

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
]
```

- [ ] **Step 6: Update `backend/config/urls.py`**

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('apps.core.urls')),
    path('blog/', include('apps.blog.urls')),
]
```

- [ ] **Step 7: Update `backend/config/settings.py`** — add near the bottom (after `STATIC_URL` or any existing block):

```python
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "blog:post_list"
LOGOUT_REDIRECT_URL = "blog:post_list"
```

- [ ] **Step 8: Write `backend/templates/registration/login.html`**

```html
{% extends "base.html" %}

{% block title %}Log in{% endblock %}

{% block content %}
<h1>Log in</h1>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Log in</button>
</form>
{% endblock %}
```

- [ ] **Step 9: Write `backend/templates/registration/signup.html`**

```html
{% extends "base.html" %}

{% block title %}Sign up{% endblock %}

{% block content %}
<h1>Sign up</h1>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Sign up</button>
</form>
{% endblock %}
```

- [ ] **Step 10: Update `backend/templates/base.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Django Playground{% endblock %}</title>
</head>
<body>
    <header>
        <h1><a href="{% url 'blog:post_list' %}">Blog</a></h1>
        <nav>
            {% if user.is_authenticated %}
                <span>{{ user.username }}</span>
                <a href="{% url 'blog:post_create' %}">New Post</a>
                <form method="post" action="{% url 'logout' %}" style="display:inline">
                    {% csrf_token %}
                    <button type="submit">Log out</button>
                </form>
            {% else %}
                <a href="{% url 'login' %}">Log in</a>
                <a href="{% url 'core:signup' %}">Sign up</a>
            {% endif %}
        </nav>
    </header>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

- [ ] **Step 11: Update `backend/apps/blog/views.py`** — replace the CRUD view classes with:

```python
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# ... keep existing imports, add the two above ...


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["title", "slug", "body", "published"]
    template_name = "blog/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ["title", "slug", "body", "published"]
    template_name = "blog/post_form.html"

    def test_func(self):
        return self.get_object().author == self.request.user


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy("blog:post_list")

    def test_func(self):
        return self.get_object().author == self.request.user
```

(The Stage-1 `get_user_model().objects.first()` hack and its `get_user_model` import are removed — no longer needed since `request.user` is available.)

- [ ] **Step 12: Run tests to verify they pass**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/core/tests.py apps/blog/ -v`
Expected: all pass.

- [ ] **Step 13: Full regression run**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/ -v`
Expected: all pass.

- [ ] **Step 14: Commit**

```bash
git add backend/apps/core/forms.py backend/apps/core/views.py backend/apps/core/urls.py backend/apps/core/tests.py backend/apps/blog/views.py backend/apps/blog/tests/test_crud_views.py backend/apps/blog/tests/test_permissions.py backend/config/urls.py backend/config/settings.py backend/templates/registration/ backend/templates/base.html
git commit -m "Add signup/login/logout and author-only edit/delete permissions"
```

---

### Task 3: Comments

**Files:**
- Modify: `backend/apps/blog/models.py`
- Create: `backend/apps/blog/migrations/0002_comment.py` (via `makemigrations`)
- Create: `backend/apps/blog/forms.py`
- Modify: `backend/apps/blog/views.py`
- Modify: `backend/apps/blog/urls.py`
- Modify: `backend/apps/blog/admin.py`
- Modify: `backend/templates/blog/post_detail.html`
- Test: `backend/apps/blog/tests/test_comments.py`

**Interfaces:**
- Consumes: `PostDetailView`, `Post` model (Task 2 / Stage 1).
- Produces: `Comment` model (`post` FK to `Post` with `related_name="comments"`, `author` FK to `AUTH_USER_MODEL`, `body` TextField, `created_at` auto). `apps.blog.forms.CommentForm` (ModelForm, `fields = ["body"]`). `CommentCreateView` (LoginRequiredMixin, CreateView) at URL name `"blog:comment_create"`, path `<slug:slug>/comments/new/`. `PostDetailView` now injects `comment_form` into context.

- [ ] **Step 1: Write the failing tests**

```python
# backend/apps/blog/tests/test_comments.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import Comment, Post


class CommentCreateViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(username="alice", password="testpass123")
        self.commenter = User.objects.create_user(username="bob", password="testpass123")
        self.post = Post.objects.create(
            title="Hello", slug="hello", body="...", author=self.author, published=True
        )

    def test_anonymous_redirected_to_login(self):
        response = self.client.post(
            reverse("blog:comment_create", kwargs={"slug": "hello"}), {"body": "Nice post"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_authenticated_user_can_comment(self):
        self.client.force_login(self.commenter)
        response = self.client.post(
            reverse("blog:comment_create", kwargs={"slug": "hello"}), {"body": "Nice post"}
        )
        self.assertRedirects(response, reverse("blog:post_detail", kwargs={"slug": "hello"}))
        comment = Comment.objects.get(post=self.post)
        self.assertEqual(comment.author, self.commenter)
        self.assertEqual(comment.body, "Nice post")

    def test_detail_page_shows_comments(self):
        Comment.objects.create(post=self.post, author=self.commenter, body="First!")
        response = self.client.get(reverse("blog:post_detail", kwargs={"slug": "hello"}))
        self.assertContains(response, "First!")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/blog/tests/test_comments.py -v`
Expected: FAIL — `ImportError: cannot import name 'Comment'`.

- [ ] **Step 3: Add `Comment` model to `backend/apps/blog/models.py`** — append after the `Post` class:

```python
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"
```

- [ ] **Step 4: Generate and apply the migration**

```bash
cd ~/django-playground/backend
.venv/bin/python manage.py makemigrations blog
.venv/bin/python manage.py migrate
```

- [ ] **Step 5: Write `backend/apps/blog/forms.py`**

```python
from django import forms

from apps.blog.models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
```

- [ ] **Step 6: Update `backend/apps/blog/views.py`** — add imports and the new view, and update `PostDetailView`:

```python
from django.shortcuts import get_object_or_404
from django.urls import reverse

from apps.blog.forms import CommentForm
from apps.blog.models import Comment, Post
```

```python
class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = CommentForm()
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, slug=self.kwargs["slug"])
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"slug": self.kwargs["slug"]})
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
    path("<slug:slug>/comments/new/", views.CommentCreateView.as_view(), name="comment_create"),
    path("<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
]
```

- [ ] **Step 8: Update `backend/apps/blog/admin.py`** — register `Comment`:

```python
from django.contrib import admin

from apps.blog.models import Comment, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published", "created_at")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_at")
```

- [ ] **Step 9: Update `backend/templates/blog/post_detail.html`**

```html
{% extends "base.html" %}

{% block title %}{{ post.title }}{% endblock %}

{% block content %}
    <article>
        <h2>{{ post.title }}</h2>
        <p>{{ post.body }}</p>
    </article>

    <section>
        <h3>Comments</h3>
        <ul>
            {% for comment in post.comments.all %}
                <li><strong>{{ comment.author }}</strong>: {{ comment.body }}</li>
            {% empty %}
                <li>No comments yet.</li>
            {% endfor %}
        </ul>

        {% if user.is_authenticated %}
            <form method="post" action="{% url 'blog:comment_create' post.slug %}">
                {% csrf_token %}
                {{ comment_form.as_p }}
                <button type="submit">Add comment</button>
            </form>
        {% else %}
            <p><a href="{% url 'login' %}">Log in</a> to comment.</p>
        {% endif %}
    </section>
{% endblock %}
```

- [ ] **Step 10: Run tests to verify they pass**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/blog/tests/test_comments.py -v`
Expected: PASS (3 passed).

- [ ] **Step 11: Full regression run**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/ -v`
Expected: all pass.

- [ ] **Step 12: Commit**

```bash
git add backend/apps/blog/models.py backend/apps/blog/migrations/ backend/apps/blog/forms.py backend/apps/blog/views.py backend/apps/blog/urls.py backend/apps/blog/admin.py backend/templates/blog/post_detail.html backend/apps/blog/tests/test_comments.py
git commit -m "Add Comment model and comment creation on post detail page"
```

---

### Task 4: Tags

**Files:**
- Modify: `backend/apps/blog/models.py`
- Create: `backend/apps/blog/migrations/0003_tag_post_tags.py` (via `makemigrations`)
- Modify: `backend/apps/blog/views.py`
- Modify: `backend/apps/blog/urls.py`
- Modify: `backend/apps/blog/admin.py`
- Modify: `backend/templates/blog/post_list.html`
- Modify: `backend/templates/blog/post_detail.html`
- Test: `backend/apps/blog/tests/test_tags.py`

**Interfaces:**
- Consumes: `Post` model, `PostListView`, `apps.blog.urls` (Tasks 1-3 / Stage 1).
- Produces: `Tag` model (`name` CharField unique, `slug` SlugField unique). `Post.tags` M2M to `Tag` (`related_name="posts"`, `blank=True`). `TaggedPostListView` (ListView) at URL name `"blog:posts_by_tag"`, path `tags/<slug:tag_slug>/`, reuses `blog/post_list.html`, adds `tag` to context. `PostCreateView`/`PostUpdateView` `fields` now include `"tags"`.

- [ ] **Step 1: Write the failing tests**

```python
# backend/apps/blog/tests/test_tags.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import Post, Tag


class TaggedPostListViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(username="alice", password="testpass123")
        self.python_tag = Tag.objects.create(name="Python", slug="python")
        self.django_tag = Tag.objects.create(name="Django", slug="django")
        self.post = Post.objects.create(
            title="Post About Python",
            slug="post-about-python",
            body="...",
            author=self.author,
            published=True,
        )
        self.post.tags.add(self.python_tag)
        self.other_post = Post.objects.create(
            title="Post About Django",
            slug="post-about-django",
            body="...",
            author=self.author,
            published=True,
        )
        self.other_post.tags.add(self.django_tag)

    def test_lists_only_posts_with_tag(self):
        response = self.client.get(
            reverse("blog:posts_by_tag", kwargs={"tag_slug": "python"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Post About Python")
        self.assertNotContains(response, "Post About Django")

    def test_unknown_tag_404s(self):
        response = self.client.get(
            reverse("blog:posts_by_tag", kwargs={"tag_slug": "does-not-exist"})
        )
        self.assertEqual(response.status_code, 404)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/blog/tests/test_tags.py -v`
Expected: FAIL — `ImportError: cannot import name 'Tag'`.

- [ ] **Step 3: Add `Tag` model and `Post.tags` field in `backend/apps/blog/models.py`** — add `Tag` above `Post`, and add the `tags` field inside `Post`:

```python
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    published = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # ... Meta, __str__, get_absolute_url unchanged ...
```

- [ ] **Step 4: Generate and apply the migration**

```bash
cd ~/django-playground/backend
.venv/bin/python manage.py makemigrations blog
.venv/bin/python manage.py migrate
```

- [ ] **Step 5: Update `backend/apps/blog/views.py`** — add `Tag` to the models import, add `TaggedPostListView`, and add `"tags"` to the CRUD views' `fields`:

```python
from apps.blog.models import Comment, Post, Tag
```

```python
class TaggedPostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["tag_slug"])
        return Post.objects.filter(published=True, tags=self.tag)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        return context
```

In `PostCreateView` and `PostUpdateView`, change:

```python
    fields = ["title", "slug", "body", "published"]
```

to:

```python
    fields = ["title", "slug", "body", "published", "tags"]
```

- [ ] **Step 6: Update `backend/apps/blog/urls.py`**

```python
from django.urls import path

from apps.blog import views

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("new/", views.PostCreateView.as_view(), name="post_create"),
    path("tags/<slug:tag_slug>/", views.TaggedPostListView.as_view(), name="posts_by_tag"),
    path("<slug:slug>/edit/", views.PostUpdateView.as_view(), name="post_update"),
    path("<slug:slug>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path("<slug:slug>/comments/new/", views.CommentCreateView.as_view(), name="comment_create"),
    path("<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
]
```

- [ ] **Step 7: Update `backend/apps/blog/admin.py`** — register `Tag`, add `filter_horizontal` to `PostAdmin`:

```python
from django.contrib import admin

from apps.blog.models import Comment, Post, Tag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published", "created_at")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_at")
```

- [ ] **Step 8: Update `backend/templates/blog/post_list.html`**

```html
{% extends "base.html" %}

{% block title %}Posts{% endblock %}

{% block content %}
    {% if tag %}<h2>Posts tagged "{{ tag.name }}"</h2>{% endif %}
    <ul>
        {% for post in posts %}
            <li>
                <a href="{% url 'blog:post_detail' post.slug %}">{{ post.title }}</a>
            </li>
        {% empty %}
            <li>No posts yet.</li>
        {% endfor %}
    </ul>
{% endblock %}
```

- [ ] **Step 9: Update `backend/templates/blog/post_detail.html`** — insert tag display inside the `<article>` block, after the body paragraph:

```html
        <p>
            Tags:
            {% for tag in post.tags.all %}
                <a href="{% url 'blog:posts_by_tag' tag.slug %}">{{ tag.name }}</a>{% if not forloop.last %}, {% endif %}
            {% empty %}
                none
            {% endfor %}
        </p>
```

- [ ] **Step 10: Run tests to verify they pass**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/blog/tests/test_tags.py -v`
Expected: PASS (2 passed).

- [ ] **Step 11: Full regression run**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/ -v`
Expected: all pass.

- [ ] **Step 12: Commit**

```bash
git add backend/apps/blog/models.py backend/apps/blog/migrations/ backend/apps/blog/views.py backend/apps/blog/urls.py backend/apps/blog/admin.py backend/templates/blog/post_list.html backend/templates/blog/post_detail.html backend/apps/blog/tests/test_tags.py
git commit -m "Add Tag model, tag filtering, and tag display"
```

---

## After this plan

Stage 2 leaves the Blog app with real auth, comments, and tags, fully tested under pytest-django, with `factory_boy` factories available for Stage 3+ to reuse. Stage 3 (DRF fundamentals — serializers, viewsets, routers, session/token/JWT auth, exposing Blog as an API, wiring up React) gets its own plan once this one is done.
