import uuid
from random import randint
from typing import List
from uuid import UUID
from fastapi import Body
from fastapi import Depends
from fastapi import HTTPException
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.deps import get_db
from app.atms import service
from app.atms.schema import AtmShow, Filters

router = APIRouter()


@router.get('/')
async def get_atm(id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> AtmShow:
    return await service.get_atm(id, db)


@router.get('/multi')
async def get_atm_multi(skip: int, limit: int, db: AsyncSession = Depends(get_db)):
    return await service.get_multi_atm(skip=skip, limit=limit, db=db)


@router.post("/filters")
async def get_atm_by_filters(filters: Filters, db: AsyncSession = Depends(get_db)) -> list[AtmShow]:
    return await service.get_by_filters(filters, db)
