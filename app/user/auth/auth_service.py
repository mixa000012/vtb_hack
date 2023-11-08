from select import select

from app.user.jwt.base.auth import JWTAuth
from fastapi import Depends

from app.user.jwt.base.token_types import TokenType
from app.user.jwt.errors import AccessError
from app.user.jwt.utils import check_revoked, generate_device_id, try_decode_token
from app.user.auth.errors import AuthError, ErrorObj
from app.user.jwt.model import IssuedJWTToken
from app.core.store import jwt_access
from app.user.jwt.schema import JwtCreate
from app.user.auth.dto import TokensDTO, UserCredentialsDTO
from enum import Enum

from fastapi import Body
from fastapi import Depends, status
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import store
from app.core.config import settings
from app.core.deps import get_db
from app.user.auth.auth import auth_user
from app.user.auth.auth import get_current_user_from_token
from app.user.model import User
from app.user.schema import User_
from app.user.schema import UserBase
from app.user.schema import UserCreate
from app.user.schema import UserShow
from app.user.schema import UserUpdateData
from app.user.service import UserDoesntExist
from app.user.utils import get_sha256_hash
from utils.hashing import Hasher

UserAlreadyExist = HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
InvalidTokenError = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The transferred token is invalid')
IncorrectTokenType = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                   detail='The passed token does not match the required type')
TokenAlreadyRevoked = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail='This token has already been revoked')


class PortalRole(str, Enum):
    ROLE_PORTAL_USER = "ROLE_PORTAL_USER"
    ROLE_PORTAL_ADMIN = "ROLE_PORTAL_ADMIN"
    ROLE_PORTAL_SUPERADMIN = "ROLE_PORTAL_SUPERADMIN"


# from utils.security import create_access_token

class AuthService:
    def __init__(self, jwt_auth: JWTAuth) -> None:
        self._jwt_auth = jwt_auth

    async def register(self, obj: UserBase, db: AsyncSession) -> TokensDTO:
        user = await store.user.get_by_email(obj.email, db)
        if user:
            raise UserAlreadyExist
        role = await store.user.get_role(db, PortalRole.ROLE_PORTAL_USER)
        user = await store.user.create(
            db,
            obj_in=UserCreate(
                email=obj.email,
                password=Hasher.get_hashed_password(obj.password),
                admin_role=role,
            ),
        )
        access_token, refresh_token = await self._issue_tokens_for_user(user=user, db=db)

        return TokensDTO(access_token=access_token, refresh_token=refresh_token)

    async def login(self, db: AsyncSession, form_data: OAuth2PasswordRequestForm = Depends()) -> tuple[
                                                                                                     TokensDTO, None] | \
                                                                                                 tuple[None, ErrorObj]:
        user = await auth_user(nickname=form_data.username, password=form_data.password, db=db)
        if not user:
            raise UserDoesntExist

        access_token, refresh_token = await self._issue_tokens_for_user(user=user, db=db)

        return TokensDTO(access_token=access_token, refresh_token=refresh_token), None

    async def logout(self, device_id: str, db) -> None:
        await store.jwt_access.revoke_token(db=db, device_id=device_id)

    async def update_tokens(self, user: User, refresh_token: str, db) -> TokensDTO:
        payload, error = try_decode_token(jwt_auth=self._jwt_auth, token=refresh_token)

        if error:
            raise InvalidTokenError

        if payload['type'] != TokenType.REFRESH.value:
            raise IncorrectTokenType
        user_id = payload.get('sub')

        # Если обновленный токен пробуют обновить ещё раз,
        # нужно отменить все выущенные на пользователя токены и вернуть ошибку
        if await check_revoked(jti=payload.get('jti'), db=db):
            await store.jwt_access.revoke_token_from_user(db=db, user_id=user_id)
            raise TokenAlreadyRevoked

        device_id = payload['device_id']
        await store.jwt_access.revoke_token_from_user_by_device(db=db, user_id=user_id, device_id=device_id)

        access_token, refresh_token = await self._issue_tokens_for_user(db, user, device_id)

        return TokensDTO(access_token=access_token, refresh_token=refresh_token)

    async def _issue_tokens_for_user(self, db, user: User, device_id: str = generate_device_id()) -> tuple[str, str]:
        access_token = self._jwt_auth.generate_access_token(subject=str(user.user_id), payload={'device_id': device_id})
        refresh_token = self._jwt_auth.generate_refresh_token(subject=str(user.user_id),
                                                              payload={'device_id': device_id})

        raw_tokens = [self._jwt_auth.get_raw_jwt(token) for token in [access_token, refresh_token]]

        for token_payload in raw_tokens:
            await store.jwt_access.create(obj_in=JwtCreate(subject=str(user.user_id),
                                                           jti=token_payload['jti'],
                                                           device_id=device_id), db=db)

        return access_token, refresh_token


auth_service = AuthService(jwt_auth=JWTAuth())
