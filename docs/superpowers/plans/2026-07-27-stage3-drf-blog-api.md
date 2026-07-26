# Stage 3a: DRF Fundamentals — Expose Blog as API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. (This project has been executing plans directly in-session instead, per an explicit, previously-communicated exception for this solo learning repo — see prior stage execution history.)

**Goal:** Expose the Blog app (Post, Comment, Tag) as a DRF API with JWT authentication, mirroring the permission rules already enforced by the template views (anyone can read published posts, only authenticated users can write, only the author can edit/delete their own).

**Architecture:** `djangorestframework` + `djangorestframework-simplejwt` mounted under `/api/`. Serializers live in `apps/blog/serializers.py`, viewsets in `apps/blog/api.py`, a `DefaultRouter` in `apps/blog/api_urls.py`. A shared `IsAuthorOrReadOnly` permission class enforces object-level write restrictions on top of DRF's `IsAuthenticatedOrReadOnly`. This is Stage 3a (backend only) — Stage 3b (wiring up a React frontend to consume this API) gets its own plan once this one is done and verified, per the project's existing per-stage planning pattern.

**Tech Stack:** Django REST Framework, djangorestframework-simplejwt, pytest-django (continuing Stage 2's pytest-style test convention).

## Global Constraints

- Tests are pytest-style (`def test_...` + `assert`), not `TestCase` subclasses — continuing the Stage 2 convention. DB-touching tests use `@pytest.mark.django_db`.
- Existing template-based views/URLs (`/blog/...`, `/accounts/...`) are untouched — the API is additive, mounted at `/api/`.
- `Post.objects.filter(published=True)` remains the only queryset the API exposes for list/retrieve — unpublished posts are not exposed via the API (same restriction as the public template views; author-side unpublished-post access is out of scope for this stage, matching YAGNI).
- No placeholders: every step below has runnable code.

---

### Task 1: DRF + JWT bootstrap

**Files:**
- Modify: `backend/requirements-dev.txt`
- Modify: `backend/config/settings.py`
- Modify: `backend/config/urls.py`
- Create: `backend/conftest.py`
- Create: `backend/apps/core/test_api_auth.py`

**Interfaces:**
- Produces: `backend/conftest.py`'s `api_client` fixture (yields `rest_framework.test.APIClient()`) — every later API test in this plan uses it. URL names `"token_obtain_pair"` (POST `username`/`password`, returns `{"access": ..., "refresh": ...}`) and `"token_refresh"` at `/api/token/` and `/api/token/refresh/`.

- [ ] **Step 1: Write the failing test**

```python
# backend/apps/core/test_api_auth.py
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.mark.django_db
def test_obtain_token_pair(api_client):
    User = get_user_model()
    User.objects.create_user(username="alice", password="testpass123")
    response = api_client.post(
        reverse("token_obtain_pair"), {"username": "alice", "password": "testpass123"}
    )
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/core/test_api_auth.py -v`
Expected: FAIL — `fixture 'api_client' not found` (and/or `ModuleNotFoundError: No module named 'rest_framework'` until Step 3 installs it).

- [ ] **Step 3: Install DRF and simplejwt, freeze requirements**

```bash
cd ~/django-playground/backend
.venv/bin/pip install djangorestframework djangorestframework-simplejwt
.venv/bin/pip freeze > requirements-dev.txt
```

- [ ] **Step 4: Update `backend/config/settings.py`** — add `'rest_framework'` to `INSTALLED_APPS` (alongside `apps.core`, `apps.blog`), and add near the bottom (after the `LOGIN_URL`/`LOGIN_REDIRECT_URL`/`LOGOUT_REDIRECT_URL` block from Stage 2):

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
}
```

- [ ] **Step 5: Write `backend/conftest.py`**

```python
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()
```

- [ ] **Step 6: Update `backend/config/urls.py`** — add the JWT token endpoints:

```python
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('apps.core.urls')),
    path('blog/', include('apps.blog.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

- [ ] **Step 7: Run test to verify it passes**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/core/test_api_auth.py -v`
Expected: PASS (1 passed).

- [ ] **Step 8: Full regression run**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/ -v`
Expected: all pass (the 28 from Stage 2 plus this 1 = 29).

- [ ] **Step 9: Commit**

```bash
git add backend/requirements-dev.txt backend/config/settings.py backend/config/urls.py backend/conftest.py backend/apps/core/test_api_auth.py
git commit -m "Add DRF and JWT auth bootstrap"
```

---

### Task 2: Read-only Post/Tag/Comment API

**Files:**
- Create: `backend/apps/blog/serializers.py`
- Create: `backend/apps/blog/api.py`
- Create: `backend/apps/blog/api_urls.py`
- Modify: `backend/config/urls.py`
- Test: `backend/apps/blog/tests/test_api_read.py`

**Interfaces:**
- Consumes: `api_client` fixture (Task 1).
- Produces: `apps.blog.serializers.TagSerializer` (`fields = ["id", "name", "slug"]`), `CommentSerializer` (`id`, `post` writable PK, `author` read-only username, `body`, `created_at` read-only), `PostSerializer` (`id`, `title`, `slug`, `body`, `author` read-only username, `published`, `tags` writable list of slugs, `created_at`, `updated_at`). `apps.blog.api.PostViewSet`/`CommentViewSet`/`TagViewSet` (all `ReadOnlyModelViewSet` for now — Task 3 upgrades to full `ModelViewSet`). Router-generated URL names `post-list`/`post-detail`, `comment-list`/`comment-detail`, `tag-list`/`tag-detail`, mounted at `/api/posts/`, `/api/comments/`, `/api/tags/`.

- [ ] **Step 1: Write the failing tests**

```python
# backend/apps/blog/tests/test_api_read.py
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.blog.models import Post, Tag


@pytest.mark.django_db
def test_list_shows_only_published(api_client):
    User = get_user_model()
    author = User.objects.create_user(username="alice", password="testpass123")
    Post.objects.create(
        title="Published", slug="published", body="...", author=author, published=True
    )
    Post.objects.create(
        title="Draft", slug="draft", body="...", author=author, published=False
    )
    response = api_client.get(reverse("post-list"))
    assert response.status_code == 200
    titles = [post["title"] for post in response.data["results"]]
    assert titles == ["Published"]


@pytest.mark.django_db
def test_retrieve_post_includes_tags(api_client):
    User = get_user_model()
    author = User.objects.create_user(username="alice", password="testpass123")
    post = Post.objects.create(
        title="Hello", slug="hello", body="Body", author=author, published=True
    )
    tag = Tag.objects.create(name="Python", slug="python")
    post.tags.add(tag)
    response = api_client.get(reverse("post-detail", kwargs={"pk": post.pk}))
    assert response.status_code == 200
    assert response.data["title"] == "Hello"
    assert response.data["author"] == "alice"
    assert response.data["tags"] == ["python"]


@pytest.mark.django_db
def test_tag_list(api_client):
    Tag.objects.create(name="Python", slug="python")
    response = api_client.get(reverse("tag-list"))
    assert response.status_code == 200
    assert response.data["results"][0]["slug"] == "python"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/blog/tests/test_api_read.py -v`
Expected: FAIL — `NoReverseMatch` for `"post-list"` (no API urls mounted yet).

- [ ] **Step 3: Write `backend/apps/blog/serializers.py`**

```python
from rest_framework import serializers

from apps.blog.models import Comment, Post, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Comment
        fields = ["id", "post", "author", "body", "created_at"]
        read_only_fields = ["created_at"]


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    tags = serializers.SlugRelatedField(
        many=True, slug_field="slug", queryset=Tag.objects.all(), required=False
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "body",
            "author",
            "published",
            "tags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
```

- [ ] **Step 4: Write `backend/apps/blog/api.py`**

```python
from rest_framework import viewsets

from apps.blog.models import Comment, Post, Tag
from apps.blog.serializers import CommentSerializer, PostSerializer, TagSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Post.objects.filter(published=True)
    serializer_class = PostSerializer


class CommentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = Comment.objects.all()
        post_id = self.request.query_params.get("post")
        if post_id is not None:
            queryset = queryset.filter(post_id=post_id)
        return queryset
```

- [ ] **Step 5: Write `backend/apps/blog/api_urls.py`**

```python
from rest_framework.routers import DefaultRouter

from apps.blog.api import CommentViewSet, PostViewSet, TagViewSet

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")
router.register("comments", CommentViewSet, basename="comment")
router.register("tags", TagViewSet, basename="tag")

urlpatterns = router.urls
```

- [ ] **Step 6: Update `backend/config/urls.py`** — add the API include:

```python
    path('api/', include('apps.blog.api_urls')),
```

(placed after the `token_refresh` path added in Task 1)

- [ ] **Step 7: Run tests to verify they pass**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/blog/tests/test_api_read.py -v`
Expected: PASS (3 passed).

- [ ] **Step 8: Full regression run**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/ -v`
Expected: all pass.

- [ ] **Step 9: Commit**

```bash
git add backend/apps/blog/serializers.py backend/apps/blog/api.py backend/apps/blog/api_urls.py backend/config/urls.py backend/apps/blog/tests/test_api_read.py
git commit -m "Add read-only Post/Comment/Tag API"
```

---

### Task 3: Write endpoints with author-only permissions

**Files:**
- Create: `backend/apps/blog/permissions.py`
- Modify: `backend/apps/blog/api.py`
- Test: `backend/apps/blog/tests/test_api_write.py`

**Interfaces:**
- Consumes: `PostSerializer`, `CommentSerializer`, `api_client` fixture (Tasks 1-2).
- Produces: `apps.blog.permissions.IsAuthorOrReadOnly` (object-level: safe methods always allowed; unsafe methods require `obj.author == request.user`). `PostViewSet`/`CommentViewSet` become full `ModelViewSet`s with `permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]`; `perform_create` sets `author=self.request.user` on both.

- [ ] **Step 1: Write the failing tests**

```python
# backend/apps/blog/tests/test_api_write.py
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from apps.blog.models import Post


def auth_headers(user):
    token = RefreshToken.for_user(user).access_token
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


@pytest.mark.django_db
def test_anonymous_cannot_create_post(api_client):
    response = api_client.post(
        reverse("post-list"),
        {"title": "New", "slug": "new", "body": "...", "published": True},
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_authenticated_user_can_create_post(api_client):
    User = get_user_model()
    user = User.objects.create_user(username="alice", password="testpass123")
    response = api_client.post(
        reverse("post-list"),
        {"title": "New", "slug": "new", "body": "...", "published": True},
        **auth_headers(user),
    )
    assert response.status_code == 201
    post = Post.objects.get(slug="new")
    assert post.author == user


@pytest.mark.django_db
def test_non_author_cannot_update_post(api_client):
    User = get_user_model()
    author = User.objects.create_user(username="alice", password="testpass123")
    other = User.objects.create_user(username="bob", password="testpass123")
    post = Post.objects.create(
        title="Original", slug="original", body="...", author=author, published=True
    )
    response = api_client.patch(
        reverse("post-detail", kwargs={"pk": post.pk}),
        {"title": "Hacked"},
        **auth_headers(other),
    )
    assert response.status_code == 403
    post.refresh_from_db()
    assert post.title == "Original"


@pytest.mark.django_db
def test_author_can_update_own_post(api_client):
    User = get_user_model()
    author = User.objects.create_user(username="alice", password="testpass123")
    post = Post.objects.create(
        title="Original", slug="original", body="...", author=author, published=True
    )
    response = api_client.patch(
        reverse("post-detail", kwargs={"pk": post.pk}),
        {"title": "Updated"},
        **auth_headers(author),
    )
    assert response.status_code == 200
    post.refresh_from_db()
    assert post.title == "Updated"


@pytest.mark.django_db
def test_authenticated_user_can_create_comment(api_client):
    User = get_user_model()
    author = User.objects.create_user(username="alice", password="testpass123")
    commenter = User.objects.create_user(username="bob", password="testpass123")
    post = Post.objects.create(
        title="Hello", slug="hello", body="...", author=author, published=True
    )
    response = api_client.post(
        reverse("comment-list"),
        {"post": post.pk, "body": "Nice post"},
        **auth_headers(commenter),
    )
    assert response.status_code == 201
    assert response.data["author"] == "bob"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/blog/tests/test_api_write.py -v`
Expected: FAIL — `405 Method Not Allowed` on POST/PATCH (viewsets are still `ReadOnlyModelViewSet`).

- [ ] **Step 3: Write `backend/apps/blog/permissions.py`**

```python
from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
```

- [ ] **Step 4: Update `backend/apps/blog/api.py`**

```python
from rest_framework import permissions, viewsets

from apps.blog.models import Comment, Post, Tag
from apps.blog.permissions import IsAuthorOrReadOnly
from apps.blog.serializers import CommentSerializer, PostSerializer, TagSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(published=True)
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.all()
        post_id = self.request.query_params.get("post")
        if post_id is not None:
            queryset = queryset.filter(post_id=post_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/blog/tests/test_api_write.py -v`
Expected: PASS (5 passed). If `test_anonymous_cannot_create_post` reports a different status than 403 (DRF's exact anonymous-write status code depends on whether any configured authentication class sets `WWW-Authenticate` — JWTAuthentication does not, so 403 is expected, but verify against actual output and treat a consistent 401 as an equally valid outcome — adjust the assertion to match observed behavior rather than forcing a specific code).

- [ ] **Step 6: Full regression run**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/ -v`
Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add backend/apps/blog/permissions.py backend/apps/blog/api.py backend/apps/blog/tests/test_api_write.py
git commit -m "Add write endpoints with author-only permissions to Blog API"
```

---

## After this plan

The Blog app now has a full read/write JWT-authenticated API alongside its existing template views, with the same author-only write rules enforced in both places. Stage 3b (wiring up a React/Vite frontend to consume this API — login form storing the JWT, post list/detail/create/edit backed by fetch calls) gets its own plan once this one is verified end-to-end (via DRF's browsable API and/or `curl`).
