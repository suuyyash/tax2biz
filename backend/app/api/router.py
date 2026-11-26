from fastapi import APIRouter
from backend.app.api.v1.leads import router as leads_router
from backend.app.api.v1.otp import router as otp_router
from backend.app.api.v1.payments import router as payments_router
from backend.app.api.v1.trademark import router as trademark_router
from backend.app.api.v1.admin import router as admin_router

api_router = APIRouter(prefix="/v1")

api_router.include_router(leads_router)
api_router.include_router(otp_router)
api_router.include_router(payments_router)
api_router.include_router(trademark_router)
api_router.include_router(admin_router)
