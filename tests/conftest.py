from typing import Generator, Any
from uuid import uuid4

import asyncpg
import pytest
from httpx import AsyncClient
from sqlalchemy import delete, insert
from typing import AsyncGenerator

from app.user.schema import UserCreate
from utils.hashing import Hasher
from utils.security import create_access_token
from datetime import timedelta
from app.core.db.base import Base
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db
from app.main import app
from app.user.model import User, Roles, PortalRole
import asyncio
from app.core import store

engine_test = create_async_engine(
    settings.PG_DATABASE_URI,
    pool_size=settings.PG_POOL_MAX_SIZE,
    pool_recycle=settings.PG_POOL_RECYCLE,
    max_overflow=settings.PG_MAX_OVERFLOW,
    pool_pre_ping=True,
)
async_session_maker = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_test, class_=AsyncSession, expire_on_commit=False,
)


async def _get_test_db():
    try:
        # create async engine for interaction with database
        engine_test = create_async_engine(
            settings.PG_DATABASE_URI,
            pool_size=settings.PG_POOL_MAX_SIZE,
            pool_recycle=settings.PG_POOL_RECYCLE,
            max_overflow=settings.PG_MAX_OVERFLOW,
            pool_pre_ping=True,
        )
        async_session_maker = sessionmaker(
            autocommit=False, autoflush=False, bind=engine_test, class_=AsyncSession, expire_on_commit=False,
        )

        yield async_session_maker()
    finally:
        pass


app.dependency_overrides[get_db] = _get_test_db


@pytest.fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # async with engine_test.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    # yield
    # async with engine_test.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://localhost/api/v1/") as ac:
        yield ac


@pytest.fixture(autouse=True)
async def clean_table():
    async with async_session_maker() as session:
        try:
            async with session.begin():
                await session.execute(delete(User))
                await session.execute(delete(Roles))

            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e


@pytest.fixture
async def create_user_in_database():
    async def create_user_in_database(user_data):
        async with async_session_maker() as session:
            stmt = insert(Roles).values(id=uuid4(), role=PortalRole.ROLE_PORTAL_USER)
            await session.execute(stmt)
            await session.commit()
            role = await store.user.get_role(session, PortalRole.ROLE_PORTAL_USER)
            user = await store.user.create(
                session,
                obj_in=UserCreate(
                    email=user_data.get('email'),
                    password=Hasher.get_hashed_password(user_data.get('password')),
                    admin_role=role
                ))
            return user
    return create_user_in_database


def create_test_auth_headers_for_user(email: str) -> dict[str, str]:
    access_token = create_access_token(
        data={"sub": str(email)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE),
    )
    return {"Authorization": f"Bearer {access_token}"}
