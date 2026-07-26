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
