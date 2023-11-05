import uuid
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.user.jwt.base.auth import JWTAuth
from app.user.jwt.model import IssuedJWTToken
from app.core import store


def generate_device_id() -> str:
    return str(uuid.uuid4())


async def check_revoked(jti: str, db: AsyncSession) -> bool:
    jwt = await store.jwt_access.get(db=db, id=jti)
    return jwt.revoked


def try_decode_token(jwt_auth: JWTAuth, token: str) -> tuple[dict, None] | tuple[None, JWTError]:
    try:
        payload = jwt_auth.verify_token(token)
        return payload, None
    except JWTError as error:
        return None, error
