import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.core.middleware import SecurityHeadersMiddleware
from backend.app.api.router import api_router
from backend.app.api.v1.leads import router as direct_leads_router
from backend.app.api.v1.trademark import router as direct_trademark_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("tax2biz.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle hook: runs once when server starts and shuts down."""
    logger.info("Initializing Tax2Biz backend database tables...")
    await init_db()
    logger.info(f"Tax2Biz backend ready in {settings.APP_ENV} mode on port {settings.PORT}.")
    yield
    logger.info("Tax2Biz backend shutting down.")

app = FastAPI(
    title="Tax2Biz Enterprise API",
    description="Secure, production-ready backend for India company registration, trademark search & legal compliance.",
    version="2.0.0",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# 1. Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 2. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time-Ms"]
)

# 3. Mount Primary API Router under /api
app.include_router(api_router, prefix="/api")

# Backwards compatibility routes for existing frontend code
app.include_router(direct_leads_router, prefix="/api")
app.include_router(direct_trademark_router, prefix="/api")

# 4. Global Exception Handler (prevents leaking internal stack traces)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An internal server error occurred. Our engineering team has been notified.",
            "code": "INTERNAL_SERVER_ERROR"
        }
    )

# 5. Serve Static Web Frontend (HTML/CSS/JS)
workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
app.mount("/", StaticFiles(directory=workspace_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
