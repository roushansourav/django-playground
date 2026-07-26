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
