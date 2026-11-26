import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("tax2biz.security")

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Applies security headers to every HTTP response:
    - Protection against Clickjacking (X-Frame-Options: SAMEORIGIN)
    - Protection against MIME-sniffing (X-Content-Type-Options: nosniff)
    - XSS auditor activation (X-XSS-Protection: 1; mode=block)
    - Referrer Policy enforcement
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        # Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"

        # Mask Server Banner
        if "server" in response.headers:
            del response.headers["server"]

        return response
