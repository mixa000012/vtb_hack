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
from app.salepoint import service
from app.salepoint.schema import SalepointShow, Filters

router = APIRouter()


@router.get('/')
async def get_sale_point(id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> SalepointShow | None:
    return await service.get_sale_point(id, db)


@router.get('/multi')
async def get_sale_point_multi(skip: int, limit: int, db: AsyncSession = Depends(get_db)) -> List[SalepointShow]:
    return await service.get_multi_sale_point(skip=skip, limit=limit, db=db)


@router.post("/filters")
async def get_sale_point_by_filters(filters: Filters, db: AsyncSession = Depends(get_db)) -> List[SalepointShow]:
    return await service.get_by_filters(filters, db)


@router.post('/distance')
async def calculate_distance(coords: List[float]):
    results = await service.calculate_distance_and_order(coords)
    return results
