import pytest
from uuid import uuid4
from sqlalchemy import insert, select

from app.user.schema import UserCreate
from conftest import async_session_maker
from app.user.model import Roles, PortalRole
from app.core import store
from utils.hashing import Hasher
from conftest import create_test_auth_headers_for_user


async def test_delete_user(client, create_user_in_database):
    user_data = {
        "email": "string",
        "password": "string"
    }
    user = await create_user_in_database(user_data)
    response = await client.delete(
        f"/user/?user_id={user.user_id}",
        headers=create_test_auth_headers_for_user(user.user_id),
    )
    assert response.status_code == 200
    assert response.json() == {'user_id': f'{user.user_id}', 'email': f'{user_data.get("email")}'}


async def test_delete_user_not_found(client, create_user_in_database):
    user_data = {
        "email": "string",
        "password": "string"
    }
    user = await create_user_in_database(user_data)
    user_id_not_exists_user = uuid4()
    resp = await client.delete(
        f"/user/?user_id={user_id_not_exists_user}",
        headers=create_test_auth_headers_for_user(user.user_id),
    )
    assert resp.status_code == 404
    assert resp.json() == {
        "detail": f"User with id {user_id_not_exists_user} not found."
    }


async def test_delete_user_user_id_validation_error(client, create_user_in_database):
    user_data = {
        "email": "string",
        "password": "string"
    }
    user = await create_user_in_database(user_data)
    response = await client.delete(
        "/user/?user_id=123",
        headers=create_test_auth_headers_for_user(user.user_id),
    )
    assert response.status_code == 422
    data_from_response = response.json()
    assert data_from_response == {
        "detail": [
            {
                "loc": ["query", "user_id"],
                "msg": "value is not a valid uuid",
                "type": "type_error.uuid",
            }
        ]
    }


async def test_delete_user_bad_cred(client, create_user_in_database):
    user_data = {
        "email": "string",
        "password": "string"
    }
    user = await create_user_in_database(user_data)
    response = await client.delete(
        "/user/?user_id=123",
        headers=create_test_auth_headers_for_user(uuid4()),
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


async def test_delete_user_no_jwt(client, create_user_in_database):
    user_data = {
        "email": "string",
        "password": "string"
    }
    user = await create_user_in_database(user_data)
    user_id = uuid4()
    response = await client.delete(
        f"/user/?user_id={user_id}",
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
