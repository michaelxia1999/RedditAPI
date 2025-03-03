import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_sign_up(test_client: AsyncClient, created_user):
    url = "/auth/sign-up"
    _, _, user = created_user

    # username already exist
    response = await test_client.post(url=url, json=user)
    assert response.status_code == 400
    assert response.json()["message"] == "Usrname Already Exist!"

    # email already exist
    user["username"] += "1"
    response = await test_client.post(url=url, json=user)
    assert response.status_code == 400
    assert response.json()["message"] == "Email Already Exist!"

    # display name already exist
    user["email"] += "1"
    response = await test_client.post(url=url, json=user)
    assert response.status_code == 400
    assert response.json()["message"] == "Display Name Already Exist!"

    # user successfully registered
    user["display_name"] += "1"
    response = await test_client.post(url=url, json=user)
    assert response.status_code == 201


@pytest.mark.asyncio(loop_scope="session")
async def test_sign_in(test_client: AsyncClient, created_user):
    _, _, user = created_user
    url = "/auth/sign-in"
    # user not found
    response = await test_client.post(url=url, json={"username": "qwe", "password": "abc"})
    assert response.status_code == 401
    assert response.json()["message"] == "Authentication Failed!"

    # user successfully sign in
    response = await test_client.post(
        url=url, json={"username": user["username"], "password": user["password"]}
    )
    assert response.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_sign_out(test_client: AsyncClient, created_user):
    _, refresh_token, user = created_user
    url = "/auth/sign-in"

    # user successfully sign in
    response = await test_client.post(
        url=url, json={"username": user["username"], "password": user["password"]}
    )
    assert response.status_code == 200

    url = "/auth/sign-out"
    response = await test_client.post(url=url, json={"token": refresh_token})
    assert response.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_refresh_access_token(test_client: AsyncClient, created_user):
    _, refresh_token, user = created_user
    url = "/auth/refresh"

    # user successfully retreieved
    response = await test_client.post(url=url, json={"token": refresh_token})
    assert response.status_code == 200

    response = await test_client.post(url=url, json={"token": "invalid_refresh_token"})
    assert response.status_code == 401
