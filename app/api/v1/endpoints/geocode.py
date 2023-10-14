import uuid
from random import randint
from typing import List, Tuple
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
from geocoding.geo import get_route_from_coords, suggest

router = APIRouter()


@router.post('/')
async def get_route(coords: List[List[float]]):
    return await get_route_from_coords(coords)


@router.get('/suggest')
async def suggest_address(query: str) -> list[str] | None:
    results = await suggest(query)
    return results
