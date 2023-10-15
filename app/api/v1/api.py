from fastapi import APIRouter

from app.api.v1.endpoints import atms
from app.api.v1.endpoints import geocode
from app.api.v1.endpoints import salepoint

api_router = APIRouter()
# api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(salepoint.router, prefix="/salepoint", tags=["salepoint"])
api_router.include_router(atms.router, prefix="/atms", tags=["atms"])
api_router.include_router(geocode.router, prefix="/geo", tags=["geo"])
