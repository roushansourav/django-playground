import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.mark.django_db
def test_obtain_token_pair(api_client):
    User = get_user_model()
    User.objects.create_user(username="alice", password="testpass123")
    response = api_client.post(
        reverse("token_obtain_pair"), {"username": "alice", "password": "testpass123"}
    )
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data
