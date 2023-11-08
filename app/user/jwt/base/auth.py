from jose import jwt
import uuid
from typing import Any
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.user.jwt.base.token_types import TokenType
from app.user.utils import convert_to_timestamp


class JWTAuth:
    def __init__(self) -> None:
        self._config = settings

    def generate_unlimited_access_token(self, subject: str, payload: dict[str, Any] = {}) -> str:
        return self.__sign_token(type=TokenType.ACCESS.value, subject=subject, payload=payload)

    def generate_access_token(self, subject: str, payload: dict[str, Any] = {}) -> str:
        return self.__sign_token(
            type=TokenType.ACCESS.value,
            subject=subject,
            payload=payload,
            expires_delta=self._config.access_token_ttl,
        )

    def generate_refresh_token(self, subject: str, payload: dict[str, Any] = {}) -> str:
        return self.__sign_token(
            type=TokenType.REFRESH.value,
            subject=subject,
            payload=payload,
            expires_delta=self._config.refresh_token_ttl,
        )

    def __sign_token(self, type: str, payload: dict[str, Any], subject: str, expires_delta: timedelta | None):
        to_encode = payload.copy()
        current_timestamp = convert_to_timestamp(datetime.now(tz=timezone.utc))
        data = dict(
            iss='befunny@auth_service',
            sub=subject,
            type=type,
            jti=self.__generate_jti(),
            iat=current_timestamp,
        )
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
        to_encode.update({"exp": expire})
        to_encode.update(data)
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY_, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def __generate_jti() -> str:
        return str(uuid.uuid4())

    def verify_token(self, token) -> dict[str, Any]:
        return jwt.decode(token, self._config.SECRET_KEY_, algorithms=[self._config.ALGORITHM])

    def get_jti(self, token) -> str:
        return self.verify_token(token)['jti']

    def get_sub(self, token) -> str:
        return self.verify_token(token)['sub']

    def get_exp(self, token) -> int:
        return self.verify_token(token)['exp']

    @staticmethod
    def get_raw_jwt(token) -> dict[str, Any]:
        """
        Return the payload of the token without checking the validity of the token
        """
        return jwt.decode(
            token, settings.SECRET_KEY_, algorithms=[settings.ALGORITHM]
        )
