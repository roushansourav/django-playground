from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import Post


class PostCreateViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(username="alice", password="testpass123")
        self.client.force_login(self.author)

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
        self.client.force_login(self.author)

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
        self.client.force_login(self.author)

    def test_post_deletes(self):
        response = self.client.post(
            reverse("blog:post_delete", kwargs={"slug": "to-delete"})
        )
        self.assertFalse(Post.objects.filter(slug="to-delete").exists())
        self.assertRedirects(response, reverse("blog:post_list"))
