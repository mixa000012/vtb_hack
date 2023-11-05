from uuid import UUID

from fastapi import Depends
from fastapi import HTTPException
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.user import service
from app.user.auth.auth import get_current_user_from_token
from app.user.model import User
from app.user.schema import TokenData
from app.user.schema import UserBase
from app.user.schema import UserShow
from app.user.service import UserAlreadyExist
from app.user.service import UserDoesntExist
from app.user.auth.auth_service import auth_service
from app.user.auth.schema import TokensOut

router = APIRouter()


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


@router.post("/users")
async def create_user(obj: UserBase, db: AsyncSession = Depends(get_db)) -> UserShow:
    try:
        user = await service.create_user(obj, db)
    except UserAlreadyExist:
        raise HTTPException(status_code=409, detail="User already exists")
    return user


@router.post('/register')
async def register(
        obj: UserBase, db: AsyncSession = Depends(get_db)
) -> TokensOut:
    data, error = await auth_service.register(obj=obj, db=db)
    return data


@router.delete("/")
async def delete_user(
        user_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token),
) -> UserShow:
    try:
        deleted_user = await service.delete_user(user_id, db, current_user)
    except UserDoesntExist:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
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
