#!/usr/bin/env python3
"""
Tax2Biz Production & Development Server Runner
Run with:
    ./venv/bin/python run_backend.py
or
    python3 run_backend.py
"""
import os
import sys

# Ensure project root is in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import uvicorn
from backend.app.core.config import settings

def main():
    print("=" * 65)
    print(" 🚀 Starting Tax2Biz Enterprise Backend Server")
    print(f" • Mode: {settings.APP_ENV} (Payment: {settings.PAYMENT_MODE}, Notifier: {settings.NOTIFICATION_MODE})")
    print(f" • Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    print(f" • Local URL: http://localhost:{settings.PORT}")
    print(f" • Swagger Docs: http://localhost:{settings.PORT}/api/docs")
    print(f" • Landing Page: http://localhost:{settings.PORT}/private-limited-company-registration.html")
    print("=" * 65)
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

if __name__ == "__main__":
    main()
