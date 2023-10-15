import uuid
from typing import List

from fastapi import Depends
from fastapi import HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.salepoint import service
from app.salepoint.schema import Filters
from app.salepoint.schema import SalepointShow
from app.salepoint.schema import SalepointShowWithDistance
from app.salepoint.service import OfficeDoesntExist

router = APIRouter()


@router.get("/")
async def get_sale_point(
    id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> SalepointShow:
    try:
        return await service.get_sale_point(id, db)
    except OfficeDoesntExist:
        raise HTTPException(status_code=404, detail="Attends not found")


@router.get("/multi")
async def get_sale_point_multi(
    skip: int, limit: int, db: AsyncSession = Depends(get_db)
) -> List[SalepointShow]:
    try:
        return await service.get_multi_sale_point(skip=skip, limit=limit, db=db)
    except OfficeDoesntExist:
        raise HTTPException(status_code=404, detail="Attends not found")


@router.post("/filters")
async def get_sale_point_by_filters(
    filters: Filters, db: AsyncSession = Depends(get_db)
) -> List[SalepointShow]:
    try:
        return await service.get_by_filters(filters, db)
    except OfficeDoesntExist:
        raise HTTPException(status_code=404, detail="Attends not found")


@router.post("/distance")
async def find_closest_offices(
    coords: List[float], db: AsyncSession = Depends(get_db)
) -> List[SalepointShowWithDistance]:
    results = await service.calculate_distance_and_order(coords, db)
    return results
