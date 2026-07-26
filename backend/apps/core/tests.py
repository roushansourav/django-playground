from django.contrib.auth import get_user_model
from django.test import TestCase


class UserModelTests(TestCase):
    def test_auth_user_model_is_core_user(self):
        User = get_user_model()
        self.assertEqual(User.__name__, "User")
        self.assertEqual(User._meta.app_label, "core")

    def test_can_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(username="alice", password="testpass123")
        self.assertTrue(user.check_password("testpass123"))
