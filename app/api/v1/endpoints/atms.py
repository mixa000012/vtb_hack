import uuid
from typing import List

from fastapi import Depends
from fastapi import HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.atms import service
from app.atms.schema import AtmShow
from app.atms.schema import AtmShowWithDistance
from app.atms.schema import Filters
from app.atms.service import AtmDoesntExist
from app.core.deps import get_db

router = APIRouter()


@router.get("/")
async def get_atm(id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> AtmShow:
    try:
        return await service.get_atm(id, db)
    except AtmDoesntExist:
        raise HTTPException(status_code=404, detail="Atm not found")


@router.get("/multi")
async def get_atm_multi(skip: int, limit: int, db: AsyncSession = Depends(get_db)):
    try:
        return await service.get_multi_atm(skip=skip, limit=limit, db=db)
    except AtmDoesntExist:
        raise HTTPException(status_code=404, detail="Atm not found")


@router.post("/filters")
async def get_atm_by_filters(
    filters: Filters, db: AsyncSession = Depends(get_db)
) -> list[AtmShow]:
    try:
        return await service.get_by_filters(filters, db)
    except AtmDoesntExist:
        raise HTTPException(status_code=404, detail="Atm not found")


@router.post("/distance")
async def find_closest_atms(
    coords: List[float], db: AsyncSession = Depends(get_db)
) -> List[AtmShowWithDistance]:
    results = await service.calculate_distance_and_order(coords, db)
    return results
