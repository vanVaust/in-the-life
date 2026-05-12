from fastapi import APIRouter
from app.api.v1.endpoints import geo, knowledge, treemap, health

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router, tags=["health"])
api_router.include_router(geo.router, prefix="/geo", tags=["geo"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(treemap.router, prefix="/treemap", tags=["treemap"])
