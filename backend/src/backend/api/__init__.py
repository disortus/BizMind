from fastapi import APIRouter
from backend.api.auth import router as auth_router
from backend.api.dashboard import router as dashboard_router
from backend.api.finances import router as finances_router
from backend.api.purchases import router as purchases_router
from backend.api.suppliers import router as suppliers_router
from backend.api.forecast import router as forecast_router
from backend.api.notifications import router as notifications_router
from backend.api.imports import router as imports_router
from backend.api.demo import router as demo_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(dashboard_router)
api_router.include_router(finances_router)
api_router.include_router(purchases_router)
api_router.include_router(suppliers_router)
api_router.include_router(forecast_router)
api_router.include_router(notifications_router)
api_router.include_router(imports_router)
api_router.include_router(demo_router)

__all__ = ["api_router"]
