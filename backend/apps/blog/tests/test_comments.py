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
