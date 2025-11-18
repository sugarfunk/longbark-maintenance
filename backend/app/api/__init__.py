from fastapi import APIRouter
from app.api.routes import sites, monitoring, seo, alerts, auth, clients, reports

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(sites.router, prefix="/sites", tags=["sites"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(seo.router, prefix="/seo", tags=["seo"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

__all__ = ["api_router"]
