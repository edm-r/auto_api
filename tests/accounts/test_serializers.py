import pytest
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from accounts.serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UpdateUserSerializer,
)


@pytest.mark.django_db
def test_validate_password_mismatch_invalid_data(valid_register_payload):
    payload = {**valid_register_payload, "password2": "DifferentPass123!"}
    serializer = RegisterSerializer(data=payload)

    is_valid = serializer.is_valid()

    assert is_valid is False
    assert "password" in serializer.errors


@pytest.mark.django_db
def test_validate_duplicate_email_invalid_data(make_user, valid_register_payload):
    make_user(username="existing", email=valid_register_payload["email"])
    serializer = RegisterSerializer(data=valid_register_payload)

    is_valid = serializer.is_valid()

    assert is_valid is False
    assert "email" in serializer.errors


@pytest.mark.django_db
def test_create_success(valid_register_payload):
    serializer = RegisterSerializer(data=valid_register_payload)

    is_valid = serializer.is_valid()

    assert is_valid is True
    user = serializer.save()
    assert user.username == valid_register_payload["username"]
    assert user.email == valid_register_payload["email"]
    assert user.check_password(valid_register_payload["password"]) is True


@pytest.mark.django_db
def test_get_token_success(make_user):
    user = make_user(username="token-user", email="token-user@example.com")

    token = CustomTokenObtainPairSerializer.get_token(user)

    assert token["username"] == user.username
    assert token["email"] == user.email


@pytest.mark.django_db
def test_validate_success(make_user):
    password = "StrongPass123!"
    user = make_user(
        username="jwt-user",
        email="jwt-user@example.com",
        password=password,
    )
    serializer = CustomTokenObtainPairSerializer(
        data={"username": user.username, "password": password}
    )

    is_valid = serializer.is_valid()

    assert is_valid is True
    assert "access" in serializer.validated_data
    assert "refresh" in serializer.validated_data
    assert serializer.validated_data["user"]["id"] == user.id
    assert serializer.validated_data["user"]["username"] == user.username


@pytest.mark.django_db
def test_validate_invalid_data(make_user):
    user = make_user(
        username="jwt-invalid-user",
        email="jwt-invalid-user@example.com",
        password="StrongPass123!",
    )
    serializer = CustomTokenObtainPairSerializer(
        data={"username": user.username, "password": "WrongPass123!"}
    )

    with pytest.raises(AuthenticationFailed):
        serializer.is_valid()


@pytest.mark.django_db
def test_validate_new_password_mismatch_invalid_data(api_request_factory, make_user):
    user = make_user(username="change-pass-user", email="change-pass-user@example.com")
    request = api_request_factory.post("/api/auth/users/change-password/", {})
    request.user = user
    serializer = ChangePasswordSerializer(
        data={
            "old_password": "StrongPass123!",
            "new_password": "NewStrongPass123!",
            "new_password2": "OtherStrongPass123!",
        },
        context={"request": request},
    )

    is_valid = serializer.is_valid()

    assert is_valid is False
    assert "new_password" in serializer.errors


@pytest.mark.django_db
def test_validate_old_password_invalid_data(api_request_factory, make_user):
    user = make_user(
        username="old-pass-user",
        email="old-pass-user@example.com",
        password="StrongPass123!",
    )
    request = api_request_factory.post("/api/auth/users/change-password/", {})
    request.user = user
    serializer = ChangePasswordSerializer(context={"request": request})

    with pytest.raises(serializers.ValidationError):
        serializer.validate_old_password("WrongPass123!")


@pytest.mark.django_db
def test_save_success(api_request_factory, make_user):
    user = make_user(
        username="save-pass-user",
        email="save-pass-user@example.com",
        password="StrongPass123!",
    )
    request = api_request_factory.post("/api/auth/users/change-password/", {})
    request.user = user
    serializer = ChangePasswordSerializer(
        data={
            "old_password": "StrongPass123!",
            "new_password": "NewStrongPass123!",
            "new_password2": "NewStrongPass123!",
        },
        context={"request": request},
    )

    is_valid = serializer.is_valid()

    assert is_valid is True
    saved_user = serializer.save()
    saved_user.refresh_from_db()
    assert saved_user.check_password("NewStrongPass123!") is True


@pytest.mark.django_db
def test_validate_email_invalid_data(api_request_factory, make_user):
    make_user(username="other-user", email="taken@example.com")
    user = make_user(username="target-user", email="target@example.com")
    request = api_request_factory.put("/api/auth/users/me/", {})
    request.user = user
    serializer = UpdateUserSerializer(
        instance=user,
        data={"email": "taken@example.com"},
        partial=True,
        context={"request": request},
    )

    is_valid = serializer.is_valid()

    assert is_valid is False
    assert "email" in serializer.errors


@pytest.mark.django_db
def test_validate_email_edge_case(api_request_factory, make_user):
    user = make_user(username="same-email-user", email="same@example.com")
    request = api_request_factory.put("/api/auth/users/me/", {})
    request.user = user
    serializer = UpdateUserSerializer(
        instance=user,
        data={"email": "same@example.com"},
        partial=True,
        context={"request": request},
    )

    is_valid = serializer.is_valid()

    assert is_valid is True
    assert serializer.validated_data["email"] == "same@example.com"
