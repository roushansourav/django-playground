import pytest

from apps.blog.factories import PostFactory


@pytest.mark.django_db
def test_post_factory_creates_valid_post():
    post = PostFactory()
    assert post.pk is not None
    assert post.published is False
    assert post.author.pk is not None
