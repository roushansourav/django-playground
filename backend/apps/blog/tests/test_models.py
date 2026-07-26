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
