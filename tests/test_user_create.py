from uuid import uuid4

import pytest
from conftest import async_session_maker
from sqlalchemy import insert
from sqlalchemy import select

from app.core import store
from app.user.model import PortalRole
from app.user.model import Roles
from utils.hashing import Hasher


async def test_add_role():
    async with async_session_maker() as session:
        stmt = insert(Roles).values(id=uuid4(), role=PortalRole.ROLE_PORTAL_ADMIN)
        await session.execute(stmt)
        await session.commit()
        stmt = insert(Roles).values(id=uuid4(), role=PortalRole.ROLE_PORTAL_USER)
        await session.execute(stmt)
        await session.commit()
        query = select(Roles)
        result = await session.execute(query)
        assert ([i.role for i in result.scalars()]) == [
            "ROLE_PORTAL_ADMIN",
            "ROLE_PORTAL_USER",
        ]


async def test_register(client):
    async with async_session_maker() as session:
        stmt = insert(Roles).values(id=uuid4(), role=PortalRole.ROLE_PORTAL_USER)
        await session.execute(stmt)
        await session.commit()
    response = await client.post(
        "user/users", json={"email": "string", "password": "string"}
    )
    result = response.json()
    async with async_session_maker() as session:
        user = await store.user.get(session, result.get("user_id"))
    assert user.email == result.get("email")
    assert Hasher.verify_password("string", user.password)
    assert user.admin_role.role == PortalRole.ROLE_PORTAL_USER
    assert str(user.user_id) == result.get("user_id")
    assert result.get("email") == "string"
    assert response.status_code == 200


async def test_create_user_duplicate_email_error(client):
    user_data = {"email": "string", "password": "string"}
    user_data_same = {"email": "string", "password": "string"}
    response = await client.post("/user/users", json=user_data)
    assert response.status_code == 200
    response = await client.post("/user/users", json=user_data_same)
    assert response.status_code == 409
    assert "User already exists" in response.json()["detail"]


@pytest.mark.parametrize(
    "user_data_for_creation, expected_status_code, expected_detail",
    [
        (
            {},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "email"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    },
                    {
                        "loc": ["body", "password"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    },
                ]
            },
        ),
        (
            {"email": 123, "password": 456},
            422,
            {"detail": "Name should contains only letters"},
        ),
    ],
)
async def test_create_user_validation_error(
    client, user_data_for_creation, expected_status_code, expected_detail
):
    response = await client.post("/user/users", json=user_data_for_creation)
    result = response.json()
    assert response.status_code == expected_status_code
    assert result == expected_detail
