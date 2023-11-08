from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.CRUD import ModelAccessor
from app.user.jwt.model import IssuedJWTToken
from app.user.jwt.schema import JwtCreate
from app.user.model import User


class JwtAccessor(ModelAccessor[IssuedJWTToken, JwtCreate, JwtCreate]):
    async def revoke_token(self, db: AsyncSession, device_id: str):
        token = await db.execute(select(IssuedJWTToken).where(IssuedJWTToken.device_id == device_id))
        token = token.scalar()
        token.revoked = True
        await db.commit()

    async def revoke_token_from_user(self, db: AsyncSession, user_id: str):
        tokens = await db.execute(
            select(IssuedJWTToken)
            .join(User.tokens)  # Присоединяем таблицу User.tokens
            .where(User.user_id == user_id)
        )
        tokens = tokens.scalars()
        for token in tokens:
            token.revoked = True
        await db.commit()

    async def revoke_token_from_user_by_device(self, db: AsyncSession, user_id: str, device_id: str):
        tokens = await db.execute(
            select(IssuedJWTToken)
            .join(User.tokens)  # Присоединяем таблицу User.tokens
            .where(and_(User.user_id == user_id, IssuedJWTToken.device_id == device_id))
        )
        tokens = tokens.scalars()
        for token in tokens:
            token.revoked = True
        await db.commit()


jwt_access = JwtAccessor(IssuedJWTToken)
