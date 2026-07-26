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
