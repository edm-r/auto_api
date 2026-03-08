import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.test import force_authenticate

from accounts.serializers import CustomTokenObtainPairSerializer
from accounts.views import CustomTokenObtainPairView, RegisterViewSet, UserViewSet


@pytest.mark.django_db
def test_get_queryset_edge_case():
    viewset = RegisterViewSet()
    viewset.action = "list"

    queryset = viewset.get_queryset()

    assert queryset.count() == 0


@pytest.mark.django_db
def test_get_queryset_success(make_user):
    make_user(username="query-user", email="query-user@example.com")
    viewset = RegisterViewSet()
    viewset.action = "create"

    queryset = viewset.get_queryset()

    assert queryset.count() == User.objects.count()


@pytest.mark.django_db
def test_register_success(api_request_factory, valid_register_payload):
    view = RegisterViewSet.as_view({"post": "register"})
    request = api_request_factory.post(
        "/api/auth/register/register/", valid_register_payload, format="json"
    )

    response = view(request)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["message"] == "Utilisateur créé avec succès."
    assert response.data["user"]["username"] == valid_register_payload["username"]
    assert User.objects.filter(username=valid_register_payload["username"]).exists() is True


@pytest.mark.django_db
def test_create_success(api_request_factory, valid_register_payload):
    view = RegisterViewSet.as_view({"post": "create"})
    request = api_request_factory.post("/api/auth/register/", valid_register_payload, format="json")

    response = view(request)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["user"]["email"] == valid_register_payload["email"]


def test_serializer_class_success():
    assert CustomTokenObtainPairView.serializer_class is CustomTokenObtainPairSerializer


def test_get_permissions_edge_case():
    viewset = UserViewSet()
    viewset.action = "list"

    permissions = viewset.get_permissions()

    assert len(permissions) == 1
    assert isinstance(permissions[0], IsAdminUser)


def test_get_permissions_success():
    viewset = UserViewSet()
    viewset.action = "update"

    permissions = viewset.get_permissions()

    assert len(permissions) == 1
    assert isinstance(permissions[0], IsAuthenticated)


@pytest.mark.django_db
def test_get_object_success(api_request_factory, make_user):
    user = make_user(username="me-user", email="me-user@example.com")
    request = api_request_factory.get("/api/auth/users/me/")
    request.user = user
    viewset = UserViewSet()
    viewset.request = request
    viewset.kwargs = {"pk": "me"}

    obj = viewset.get_object()

    assert obj.id == user.id


@pytest.mark.django_db
def test_retrieve_success(api_request_factory, make_user):
    user = make_user(username="retrieve-user", email="retrieve-user@example.com")
    view = UserViewSet.as_view({"get": "retrieve"})
    request = api_request_factory.get("/api/auth/users/me/")
    force_authenticate(request, user=user)

    response = view(request, pk="me")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == user.id
    assert response.data["email"] == user.email


@pytest.mark.django_db
def test_update_non_owner_edge_case(api_request_factory, make_user):
    target_user = make_user(username="target-user", email="target-user@example.com")
    current_user = make_user(username="current-user", email="current-user@example.com")
    view = UserViewSet.as_view({"put": "update"})
    request = api_request_factory.put(
        f"/api/auth/users/{target_user.id}/",
        {
            "username": target_user.username,
            "email": "updated-target@example.com",
            "first_name": "First",
            "last_name": "Last",
        },
        format="json",
    )
    force_authenticate(request, user=current_user)

    response = view(request, pk=target_user.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"] == "Vous n'avez pas le droit de modifier cet utilisateur."


@pytest.mark.django_db
def test_update_success(api_request_factory, make_user):
    user = make_user(username="owner-user", email="owner-user@example.com")
    view = UserViewSet.as_view({"put": "update"})
    request = api_request_factory.put(
        f"/api/auth/users/{user.id}/",
        {
            "username": "owner-user-updated",
            "email": "owner-user-updated@example.com",
            "first_name": "Owner",
            "last_name": "Updated",
        },
        format="json",
    )
    force_authenticate(request, user=user)

    response = view(request, pk=user.id)

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.username == "owner-user-updated"
    assert user.email == "owner-user-updated@example.com"


@pytest.mark.django_db
def test_update_edge_case(api_request_factory, make_user):
    target_user = make_user(username="staff-target", email="staff-target@example.com")
    admin_user = make_user(
        username="staff-editor",
        email="staff-editor@example.com",
        is_staff=True,
    )
    view = UserViewSet.as_view({"put": "update"})
    request = api_request_factory.put(
        f"/api/auth/users/{target_user.id}/",
        {
            "username": target_user.username,
            "email": "staff-target-updated@example.com",
            "first_name": "Staff",
            "last_name": "Allowed",
        },
        format="json",
    )
    force_authenticate(request, user=admin_user)

    response = view(request, pk=target_user.id)

    assert response.status_code == status.HTTP_200_OK
    target_user.refresh_from_db()
    assert target_user.email == "staff-target-updated@example.com"


@pytest.mark.django_db
def test_destroy_non_owner_edge_case(api_request_factory, make_user):
    target_user = make_user(username="delete-target", email="delete-target@example.com")
    current_user = make_user(username="delete-current", email="delete-current@example.com")
    view = UserViewSet.as_view({"delete": "destroy"})
    request = api_request_factory.delete(f"/api/auth/users/{target_user.id}/")
    force_authenticate(request, user=current_user)

    response = view(request, pk=target_user.id)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"] == "Vous n'avez pas le droit de supprimer cet utilisateur."


@pytest.mark.django_db
def test_destroy_success(api_request_factory, make_user):
    user = make_user(username="delete-owner", email="delete-owner@example.com")
    view = UserViewSet.as_view({"delete": "destroy"})
    request = api_request_factory.delete(f"/api/auth/users/{user.id}/")
    force_authenticate(request, user=user)

    response = view(request, pk=user.id)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert User.objects.filter(pk=user.id).exists() is False


@pytest.mark.django_db
def test_me_unauthenticated(api_request_factory):
    view = UserViewSet.as_view({"get": "me"})
    request = api_request_factory.get("/api/auth/users/me/")

    response = view(request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_me_success(api_request_factory, make_user):
    user = make_user(username="me-get", email="me-get@example.com")
    view = UserViewSet.as_view({"get": "me"})
    request = api_request_factory.get("/api/auth/users/me/")
    force_authenticate(request, user=user)

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["username"] == user.username


@pytest.mark.django_db
def test_me_put_success(api_request_factory, make_user):
    user = make_user(username="me-put", email="me-put@example.com")
    view = UserViewSet.as_view({"put": "me"})
    request = api_request_factory.put(
        "/api/auth/users/me/",
        {"email": "me-put-updated@example.com", "first_name": "Updated"},
        format="json",
    )
    force_authenticate(request, user=user)

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Profil mis à jour avec succès."
    user.refresh_from_db()
    assert user.email == "me-put-updated@example.com"
    assert user.first_name == "Updated"


@pytest.mark.django_db
def test_me_put_invalid_data(api_request_factory, make_user):
    make_user(username="email-owner", email="already-used@example.com")
    user = make_user(username="email-updater", email="email-updater@example.com")
    view = UserViewSet.as_view({"put": "me"})
    request = api_request_factory.put(
        "/api/auth/users/me/",
        {"email": "already-used@example.com"},
        format="json",
    )
    force_authenticate(request, user=user)

    response = view(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


@pytest.mark.django_db
def test_change_password_success(api_request_factory, make_user):
    user = make_user(
        username="change-pass",
        email="change-pass@example.com",
        password="StrongPass123!",
    )
    view = UserViewSet.as_view({"post": "change_password"})
    request = api_request_factory.post(
        "/api/auth/users/change-password/",
        {
            "old_password": "StrongPass123!",
            "new_password": "NewStrongPass123!",
            "new_password2": "NewStrongPass123!",
        },
        format="json",
    )
    force_authenticate(request, user=user)

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.check_password("NewStrongPass123!") is True


@pytest.mark.django_db
def test_change_password_invalid_data(api_request_factory, make_user):
    user = make_user(
        username="change-pass-invalid",
        email="change-pass-invalid@example.com",
        password="StrongPass123!",
    )
    view = UserViewSet.as_view({"post": "change_password"})
    request = api_request_factory.post(
        "/api/auth/users/change-password/",
        {
            "old_password": "WrongPass123!",
            "new_password": "NewStrongPass123!",
            "new_password2": "NewStrongPass123!",
        },
        format="json",
    )
    force_authenticate(request, user=user)

    response = view(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "old_password" in response.data


@pytest.mark.django_db
def test_logout_success(api_request_factory, make_user):
    user = make_user(username="logout-user", email="logout-user@example.com")
    view = UserViewSet.as_view({"post": "logout"})
    request = api_request_factory.post("/api/auth/users/logout/", {}, format="json")
    force_authenticate(request, user=user)

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Déconnecté avec succès."


@pytest.mark.django_db
def test_list_unauthenticated(api_request_factory):
    view = UserViewSet.as_view({"get": "list"})
    request = api_request_factory.get("/api/auth/users/")

    response = view(request)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_edge_case(api_request_factory, make_user):
    regular_user = make_user(username="regular-list", email="regular-list@example.com")
    view = UserViewSet.as_view({"get": "list"})
    request = api_request_factory.get("/api/auth/users/")
    force_authenticate(request, user=regular_user)

    response = view(request)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_success(api_request_factory, make_user):
    admin_user = make_user(username="admin-list", email="admin-list@example.com", is_staff=True)
    make_user(username="list-user-1", email="list-user-1@example.com")
    make_user(username="list-user-2", email="list-user-2@example.com")
    view = UserViewSet.as_view({"get": "list"})
    request = api_request_factory.get("/api/auth/users/")
    force_authenticate(request, user=admin_user)

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert "results" in response.data
    assert len(response.data["results"]) >= 3
