import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    await init_db()

@pytest.mark.asyncio
async def test_security_headers_present():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/leads")
        assert resp.status_code == 200
        # Check security headers
        assert resp.headers.get("X-Content-Type-Options") == "nosniff"
        assert resp.headers.get("X-Frame-Options") == "SAMEORIGIN"
        assert resp.headers.get("X-XSS-Protection") == "1; mode=block"
        assert "server" not in resp.headers # Server signature masked

@pytest.mark.asyncio
async def test_otp_rate_limiting():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        test_phone = "9988776655"
        # 1st request -> 200
        r1 = await client.post("/api/v1/otp/request", json={"phone": test_phone})
        assert r1.status_code == 200

        # 2nd request -> 200
        r2 = await client.post("/api/v1/otp/request", json={"phone": test_phone})
        assert r2.status_code == 200

        # 3rd request -> 200
        r3 = await client.post("/api/v1/otp/request", json={"phone": test_phone})
        assert r3.status_code == 200

        # 4th request -> Rate limited (429 Too Many Requests)
        r4 = await client.post("/api/v1/otp/request", json={"phone": test_phone})
        assert r4.status_code == 429
        assert "Too many OTP requests" in r4.json()["detail"]

@pytest.mark.asyncio
async def test_trademark_search_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/trademark/search?q=Tax2Biz&class=45")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["query"] == "Tax2Biz"
        assert "verdict" in data
        assert "records" in data
