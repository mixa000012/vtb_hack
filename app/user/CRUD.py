from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.CRUD import ModelAccessor
from app.user.model import Roles
from app.user.model import User
from app.user.schema import UserCreate
from app.user.schema import UserUpdateData


class UserAccessor(ModelAccessor[User, UserCreate, UserUpdateData]):
    async def get_by_email(self, nickname, db: AsyncSession):
        user = await db.execute(
            select(User)
            .options(selectinload(User.admin_role))
            .where(User.email == nickname)
        )
        user = user.scalar()
        return user

    async def get_role(self, db: AsyncSession, role):
        role = await db.execute(select(Roles).where(Roles.role == role))
        role = role.scalar()
        return role

    async def get(self, db: AsyncSession, user_id):
        stmt = (
            select(User)
            .options(selectinload(User.admin_role))
            .where(User.user_id == user_id)
        )
        user = await db.execute(stmt)
        user = user.scalar()
        return user


user = UserAccessor(User)
