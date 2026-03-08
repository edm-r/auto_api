import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory


@pytest.fixture
def api_request_factory():
    return APIRequestFactory()


@pytest.fixture
def make_user(db):
    def _make_user(
        username: str,
        email: str,
        password: str = "StrongPass123!",
        is_staff: bool = False,
    ):
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=is_staff,
        )

    return _make_user


@pytest.fixture
def valid_register_payload():
    return {
        "username": "new-user",
        "email": "new-user@example.com",
        "password": "StrongPass123!",
        "password2": "StrongPass123!",
        "first_name": "New",
        "last_name": "User",
    }
