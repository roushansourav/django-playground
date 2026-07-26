from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model. No extra fields yet — exists so AUTH_USER_MODEL
    can point here from project creation, avoiding an unswappable default."""
