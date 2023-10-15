from typing import List

from fastapi import HTTPException
from fastapi.routing import APIRouter
from openrouteservice.exceptions import ApiError

from geocoding.geo import get_route_from_coords
from geocoding.geo import suggest

router = APIRouter()


@router.post("/")
async def get_route(coords: List[List[float]], profile: str) -> List[List[float]]:
    try:
        res = await get_route_from_coords(coords, profile)
    except ApiError as ex:
        raise HTTPException(404, detail=f"{ex}")
    return res


@router.get("/suggest")
async def suggest_address(query: str) -> list[str] | None:
    results = await suggest(query)
    return results
