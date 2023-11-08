import re
import uuid
from enum import Enum
from typing import Any

from fastapi import HTTPException
from pydantic import validator, EmailStr
from pydantic.main import BaseModel

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class PortalRole(str, Enum):
    ROLE_PORTAL_USER = "ROLE_PORTAL_USER"
    ROLE_PORTAL_ADMIN = "ROLE_PORTAL_ADMIN"
    ROLE_PORTAL_SUPERADMIN = "ROLE_PORTAL_SUPERADMIN"


class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserCreate(UserBase):
    admin_role: Any

    # @validator("email")
    # def validate_name(cls, value):
    #     if not LETTER_MATCH_PATTERN.match(value):
    #         raise HTTPException(
    #             status_code=422, detail="Name should contains only letters"
    #         )
    #     return value


class UserUpdateData(UserBase):
    pass


class User_(UserUpdateData):
    user_id: uuid.UUID

    class Config:
        orm_mode = True


class UserShow(BaseModel):
    user_id: uuid.UUID
    email: str

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    access_token: str
    token_type: str


class LogoutResponse(BaseModel):
    success: str
