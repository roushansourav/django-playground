import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_api_response_includes_cors_header(client):
    response = client.get(reverse("post-list"), HTTP_ORIGIN="http://localhost:5173")
    assert response["Access-Control-Allow-Origin"] == "http://localhost:5173"
