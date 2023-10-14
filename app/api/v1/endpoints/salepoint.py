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
from app.salepoint.service import OfficeDoesntExist
from app.core.deps import get_db
from app.salepoint import service
from app.salepoint.schema import SalepointShow, Filters, SalepointShowWithDistance

router = APIRouter()


@router.get('/')
async def get_sale_point(id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> SalepointShow:
    try:
        return await service.get_sale_point(id, db)
    except OfficeDoesntExist:
        raise HTTPException(status_code=404, detail="Attends not found")


@router.get('/multi')
async def get_sale_point_multi(skip: int, limit: int, db: AsyncSession = Depends(get_db)) -> List[SalepointShow]:
    try:
        return await service.get_multi_sale_point(skip=skip, limit=limit, db=db)
    except OfficeDoesntExist:
        raise HTTPException(status_code=404, detail="Attends not found")


@router.post("/filters")
async def get_sale_point_by_filters(filters: Filters, db: AsyncSession = Depends(get_db)) -> List[SalepointShow]:
    try:
        return await service.get_by_filters(filters, db)
    except OfficeDoesntExist:
        raise HTTPException(status_code=404, detail="Attends not found")


@router.post('/distance')
async def find_closest_offices(coords: List[float]) -> List[SalepointShowWithDistance]:
    results = await service.calculate_distance_and_order(coords)
    return results
