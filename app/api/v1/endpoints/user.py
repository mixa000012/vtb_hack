from uuid import UUID

from fastapi import Depends, Body, status
from fastapi import HTTPException
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.user import service
from app.user.auth.auth import get_current_user_from_token, get_device_id_from_token
from app.user.model import User
from app.user.schema import TokenData, LogoutResponse
from app.user.schema import UserBase
from app.user.schema import UserShow
from app.user.service import UserAlreadyExist
from app.user.service import UserDoesntExist
from app.user.auth.auth_service import auth_service, InvalidTokenError, IncorrectTokenType, TokenAlreadyRevoked
from app.user.auth.schema import TokensOut, UpdateTokensIn

router = APIRouter()


@router.post('/register', responses={409: {
    "description": "User already exists error",
    "content": {
        "application/json": {
            "example": UserAlreadyExist
        }
    }
}})
async def register(
        obj: UserBase = Body(examples=[
            {
                'email': 'user@mail.ru',
                'password': 'password'
            }
        ]), db: AsyncSession = Depends(get_db)
) -> TokensOut:
    data = await auth_service.register(obj=obj, db=db)
    return data


@router.post("/token")
async def login_for_token(
        form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> TokensOut:
    try:
        tokens, error = await auth_service.login(form_data=form_data, db=db)
    except UserDoesntExist:
        raise HTTPException(
            status_code=401, detail="There is no user in database with this fio"
        )
    return tokens


# @router.post("/users")
# async def create_user(obj: UserBase, db: AsyncSession = Depends(get_db)) -> UserShow:
#     try:
#         user = await service.create_user(obj, db)
#     except UserAlreadyExist:
#         raise HTTPException(status_code=409, detail="User already exists")
#     return user
@router.post('/logout', responses={200: {
    "content": {
        "application/json": {
            "example": {
                "success": "7cfe7d8f-673a-4d3b-9026-a5cb09e93333"
            }
        }
    }
}})
async def logout(current_user: User = Depends(get_current_user_from_token), db: AsyncSession = Depends(get_db),
                 device_id: str = Depends(get_device_id_from_token)) -> LogoutResponse:
    await auth_service.logout(device_id=device_id, db=db)
    return LogoutResponse(success=device_id)


@router.post('/update-tokens', responses={
    401: {
        "description": "Invalid token",
        "content": {
            "application/json": {
                "example": InvalidTokenError
            }
        }
    },
    400: {"description": "Invalid token type / Token already revoked",
          "content": {
              "Invalid token type": {
                  "example": IncorrectTokenType
              },
              "Token already revoked": {"example": TokenAlreadyRevoked}

          }}
})
async def update_tokens(body: UpdateTokensIn, current_user: User = Depends(get_current_user_from_token),
                        db: AsyncSession = Depends(get_db)) -> TokensOut:
    data = await auth_service.update_tokens(user=current_user, db=db, **body.dict())
    return data


@router.delete("/", responses={404: {
    "description": "User not found error",
    "content": {
        "application/json": {
            "example": UserDoesntExist
        }
    }
}})
async def delete_user(
        user_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token),
) -> UserShow:
    deleted_user = await service.delete_user(user_id, db, current_user)
    return deleted_user


@router.patch("/admin_privilege")
async def grant_admin_privilege(
        email: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token),
) -> UserShow:
    try:
        updated_user = await service.grant_admin_privilege(email, db, current_user)
    except IntegrityError as err:
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return updated_user


@router.delete("/admin_privilege")
async def revoke_admin_privilege(
        email: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token),
) -> UserShow:
    try:
        updated_user = await service.grant_admin_privilege(email, db, current_user)
    except IntegrityError as err:
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return updated_user


@router.get("/")
async def get_user(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token),
):
    return await service.get_user(db, current_user)
