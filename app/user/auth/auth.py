from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from app.core.config import settings
from app.core.deps import get_db
from app.user.jwt.base.token_types import TokenType
from app.user.jwt.utils import check_revoked
from app.user.model import User
from utils.hashing import Hasher

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/token")


async def get_current_user_from_token(
        token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY_, algorithms=[settings.ALGORITHM]
        )
        if payload['type'] != TokenType.ACCESS.value:
            raise HTTPException(detail='This is not access token!', status_code=403)
        if await check_revoked(payload['jti'], db):
            raise HTTPException(detail='This token is revoked!', status_code=403)
        id = payload.get("sub")
        if id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await db.execute(
        select(User).options(selectinload(User.admin_role)).where(User.user_id == id)
    )
    user = user.scalar()
    if user is None:
        raise credentials_exception
    return user


async def get_device_id_from_token(
        token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    payload = jwt.decode(
        token, settings.SECRET_KEY_, algorithms=[settings.ALGORITHM]
    )
    device_id = payload.get("device_id")
    return device_id

async def auth_user(nickname: str, password: str, db: AsyncSession) -> None | User:
    user = await db.execute(select(User).where(User.email == nickname))
    user = user.scalar()
    if not user:
        return
    if not Hasher.verify_password(password, user.password):
        return
    return user
