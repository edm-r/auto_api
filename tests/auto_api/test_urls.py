import json

import pytest
from django.urls import resolve, reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory

from auto_api.urls import root_health


def test_root_health_success(rf):
    request = rf.get("/")

    response = root_health(request)

    payload = json.loads(response.content.decode("utf-8"))
    assert response.status_code == status.HTTP_200_OK
    assert payload["message"] == "Auto API est en ligne."


def test_reverse_success():
    assert reverse("root_health") == "/"
    assert reverse("token_obtain_pair") == "/api/auth/login/"
    assert reverse("token_refresh") == "/api/auth/token/refresh/"


def test_resolve_success():
    root_match = resolve("/")
    login_match = resolve("/api/auth/login/")

    assert root_match.func == root_health
    assert login_match.url_name == "token_obtain_pair"


@pytest.mark.django_db
def test_login_success(make_user):
    password = "StrongPass123!"
    user = make_user(
        username="login-user",
        email="login-user@example.com",
        password=password,
    )
    view = resolve("/api/auth/login/").func
    request_factory = APIRequestFactory()
    request = request_factory.post(
        reverse("token_obtain_pair"),
        {"username": user.username, "password": password},
        format="json",
    )
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data
    assert response.data["user"]["id"] == user.id


@pytest.mark.django_db
def test_login_invalid_data(make_user):
    user = make_user(
        username="login-invalid",
        email="login-invalid@example.com",
        password="StrongPass123!",
    )
    view = resolve("/api/auth/login/").func
    request_factory = APIRequestFactory()
    request = request_factory.post(
        reverse("token_obtain_pair"),
        {"username": user.username, "password": "WrongPass123!"},
        format="json",
    )
    response = view(request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.data
