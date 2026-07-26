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
