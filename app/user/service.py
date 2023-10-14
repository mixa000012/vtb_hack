from enum import Enum
from datetime import timedelta
from uuid import UUID

from fastapi import Body
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import store
from app.core.deps import get_db
from app.user.auth import auth_user
from app.user.auth import get_current_user_from_token
from app.user.schema import UserShow, User_, UserBase
from app.user.schema import UserCreate, UserUpdateData
from app.core.config import settings
from utils.security import create_access_token
from utils.hashing import Hasher
from app.user.model import User


class UserDoesntExist(Exception):
    pass


class UserAlreadyExist(Exception):
    pass


class PortalRole(str, Enum):
    ROLE_PORTAL_USER = "ROLE_PORTAL_USER"
    ROLE_PORTAL_ADMIN = "ROLE_PORTAL_ADMIN"
    ROLE_PORTAL_SUPERADMIN = "ROLE_PORTAL_SUPERADMIN"


async def login_for_token(
        form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> str:
    user = await auth_user(form_data.username, form_data.password, db)
    if not user:
        raise UserDoesntExist
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
    access_token = create_access_token(
        data={"sub": str(user.user_id)},
        expires_delta=access_token_expires,
    )
    return access_token


async def create_user(obj: UserBase, db: AsyncSession = Depends(get_db)) -> UserShow:
    user = await store.user.get_by_email(obj.email, db)
    if user:
        raise UserAlreadyExist
    role = await store.user.get_role(db, PortalRole.ROLE_PORTAL_USER)
    user = await store.user.create(
        db,
        obj_in=UserCreate(
            email=obj.email,
            password=Hasher.get_hashed_password(obj.password),
            admin_role=role
        ))
    return user


async def update_user(
        current_user: User = Depends(get_current_user_from_token),
        update_data: UserUpdateData = Body(...),
        db: AsyncSession = Depends(get_db),
) -> User_:
    updated_user = await store.user.update(
        db=db,
        db_obj=current_user,
        obj_in=update_data,
    )

    return updated_user


def check_user_permissions(target_user: User, current_user: User) -> bool:
    if PortalRole.ROLE_PORTAL_SUPERADMIN == target_user.admin_role.role:
        raise HTTPException(
            status_code=406, detail="Superadmin cannot be deleted via API."
        )
    if target_user.user_id != current_user.user_id:
        # check admin role
        if not current_user.is_superadmin or current_user.is_admin:
            return False
        # check admin deactivate superadmin attempt
        if (
                target_user.is_superadmin
                and current_user.is_admin
        ):
            return False
        # check admin deactivate admin attempt
        if (
                target_user.is_admin
                and current_user.is_admin

        ):
            return False
    return True


async def delete_user(
        user_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token),
) -> UserShow:
    user_for_deletion = await store.user.get(db, user_id)
    if user_for_deletion is None:
        raise UserDoesntExist
    if not check_user_permissions(
            target_user=user_for_deletion,
            current_user=current_user,
    ):
        raise HTTPException(status_code=403, detail='forbidden.')
    deleted_user_id = await store.user.remove(db=db, id=user_id)
    if deleted_user_id is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    return user_for_deletion


async def grant_admin_privilege(
        nickname: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token),
) -> UserShow:
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Forbidden.")
    if current_user.email == nickname:
        raise HTTPException(
            status_code=400, detail="Cannot manage privileges of itself."
        )
    user_for_promotion = await store.user.get_by_email(nickname, db)
    if user_for_promotion.is_admin or user_for_promotion.is_superadmin:
        raise HTTPException(
            status_code=409,
            detail=f"User with id {nickname} already promoted to admin / superadmin.",
        )
    if user_for_promotion is None:
        raise HTTPException(
            status_code=404, detail=f"User with  {nickname} not found."
        )
    admin_role = await store.user.get_role(db, PortalRole.ROLE_PORTAL_ADMIN)
    user_for_promotion.admin_role = admin_role
    await db.commit()

    return user_for_promotion


async def revoke_admin_privilege(
        email: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_token),
):
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Forbidden.")
    if current_user.email == email:
        raise HTTPException(
            status_code=400, detail="Cannot manage privileges of itself."
        )
    user_for_revoke_admin_privileges = await store.user.get_by_email(email, db)
    if not user_for_revoke_admin_privileges.is_admin:
        raise HTTPException(
            status_code=409, detail=f"User with id {email} has no admin privileges."
        )
    if user_for_revoke_admin_privileges is None:
        raise HTTPException(
            status_code=404, detail=f"User with {email} not found."
        )
    updated_user_params = {
        "roles": user_for_revoke_admin_privileges.remove_admin_privileges_from_model()
    }
    try:
        updated_user = await store.user.update(
            db=db,
            db_obj=user_for_revoke_admin_privileges,
            obj_in=updated_user_params,
        )
    except Exception as ex:
        print(ex)
    return updated_user


async def get_user(db: AsyncSession = Depends(get_db),
                   current_user: User = Depends(get_current_user_from_token)):
    return await store.user.get(db, current_user.user_id)
