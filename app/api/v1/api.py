from fastapi import APIRouter

from app.api.v1.endpoints import user, salepoint, atms,geocode

api_router = APIRouter()
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(salepoint.router, prefix="/salepoint", tags=["salepoint"])
api_router.include_router(atms.router, prefix="/atms", tags=["atms"])
api_router.include_router(geocode.router, prefix="/geo", tags=["geo"])


