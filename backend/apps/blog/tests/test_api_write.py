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
