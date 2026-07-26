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
