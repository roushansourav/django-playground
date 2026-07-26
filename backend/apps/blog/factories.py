import factory

from apps.blog.models import Post
from apps.core.factories import UserFactory


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Faker("sentence")
    slug = factory.Sequence(lambda n: f"post-{n}")
    body = factory.Faker("paragraph")
    author = factory.SubFactory(UserFactory)
    published = False
