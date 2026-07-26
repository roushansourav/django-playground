from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class UserModelTests(TestCase):
    def test_auth_user_model_is_core_user(self):
        User = get_user_model()
        self.assertEqual(User.__name__, "User")
        self.assertEqual(User._meta.app_label, "core")

    def test_can_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(username="alice", password="testpass123")
        self.assertTrue(user.check_password("testpass123"))


class SignupViewTests(TestCase):
    def test_get_form_renders(self):
        response = self.client.get(reverse("core:signup"))
        self.assertEqual(response.status_code, 200)

    def test_post_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("core:signup"),
            {
                "username": "newuser",
                "password1": "a-very-strong-pass123",
                "password2": "a-very-strong-pass123",
            },
        )
        User = get_user_model()
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertRedirects(response, reverse("blog:post_list"))
        response2 = self.client.get(reverse("blog:post_create"))
        self.assertEqual(response2.status_code, 200)
