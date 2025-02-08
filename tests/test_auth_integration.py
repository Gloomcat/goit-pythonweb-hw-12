import pytest

from unittest.mock import patch
from conftest import test_user, test_user_register

from src.database.models import User
from src.services.email import send_email
from src.services.auth import Hash


@pytest.mark.asyncio
@patch("src.services.users.UserService.get_user_by_email")
@patch("src.services.users.UserService.get_user_by_username")
@patch("src.services.users.UserService.create_user")
@patch("fastapi.BackgroundTasks.add_task")
async def test_register_user(
    mock_add_task,
    mock_create_user,
    mock_get_user_by_username,
    mock_get_user_by_email,
    client,
):
    mock_get_user_by_email.return_value = None
    mock_get_user_by_username.return_value = None
    mock_create_user.return_value = User(
        id=1,
        username=test_user_register["username"],
        email=test_user_register["email"],
        avatar=test_user_register["avatar"],
        confirmed=False,
    )

    response = client.post("/api/auth/register", json=test_user_register)

    assert response.status_code == 201, response.text

    data = response.json()
    assert data["username"] == test_user_register["username"]
    assert data["email"] == test_user_register["email"]
    assert "avatar" in data

    mock_create_user.assert_called_once()
    mock_add_task.assert_called_once_with(
        send_email,
        test_user_register["email"],
        test_user_register["username"],
        "http://testserver/",
    )


@pytest.mark.asyncio
@patch("src.services.users.UserService.get_user_by_username")
@patch("src.services.auth.Hash.verify_password")
@patch(
    "src.api.auth.create_access_token"
)  # apply patch to imported function in a module, not original
async def test_login_user(
    mock_create_token,
    mock_verify_password,
    mock_get_user_by_username,
    client,
    get_token,
):
    token = get_token
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"],
    }

    mock_get_user_by_username.return_value = User(
        id=1,
        username=test_user["username"],
        email=test_user["email"],
        hashed_password=Hash().get_password_hash(test_user["password"]),
        avatar=test_user["avatar"],
        confirmed=True,
    )
    mock_verify_password.return_value = True
    mock_create_token.return_value = token

    response = client.post("/api/auth/login", data=login_data)

    assert response.status_code == 201, response.text
    data = response.json()

    assert data["access_token"] == token
    assert data["token_type"] == "bearer"

    mock_verify_password.assert_called_once()
    mock_create_token.assert_called_once()


@pytest.mark.asyncio
@patch(
    "src.api.auth.get_email_from_token"
)  # apply patch to imported function in a module, not original
@patch("src.services.users.UserService.get_user_by_email")
@patch("src.services.users.UserService.confirmed_email")
async def test_confirmed_email(
    mock_confirm_email, mock_get_user, mock_get_email, client, get_token
):
    token = get_token

    mock_get_email.return_value = test_user["email"]
    mock_get_user.return_value = User(
        id=1,
        username=test_user["username"],
        email=test_user["email"],
        hashed_password=Hash().get_password_hash(test_user["password"]),
        avatar=test_user["avatar"],
        confirmed=True,
    )
    mock_confirm_email.return_value = None  # Simulate successful confirmation

    response = client.get(f"/api/auth/confirmed_email/{token}")

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Your email is already verified"

    mock_get_user.assert_called_once()
    mock_get_email.assert_called_once()


@pytest.mark.asyncio
@patch("src.services.users.UserService.get_user_by_email")
@patch("src.services.email.send_email")
async def test_request_email_verification(mock_send_email, mock_get_user, client):
    request_data = {"email": test_user["email"]}

    mock_get_user.return_value = User(
        id=1,
        username=test_user["username"],
        email=test_user["email"],
        hashed_password=Hash().get_password_hash(test_user["password"]),
        avatar=test_user["avatar"],
        confirmed=True,
    )

    response = client.post("/api/auth/request_email", json=request_data)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Your email is already verified"

    mock_get_user.assert_called_once()
    # Since email is already verified, email shouldn't be sent
    mock_send_email.assert_not_called()
