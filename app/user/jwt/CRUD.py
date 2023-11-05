from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db.CRUD import ModelAccessor
from app.user.jwt.model import IssuedJWTToken
from app.user.jwt.schema import JwtCreate


class JwtAccessor(ModelAccessor[IssuedJWTToken, JwtCreate, JwtCreate]):
    pass


jwt_access = JwtAccessor(IssuedJWTToken)
