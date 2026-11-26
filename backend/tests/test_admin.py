import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    await init_db()

@pytest.mark.asyncio
async def test_admin_portal_workflow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Reject invalid admin login
        bad_login = await client.post("/api/v1/admin/login", json={
            "email": "admin@tax2biz.in",
            "password": "wrong_password"
        })
        assert bad_login.status_code == 401

        # 2. Accept valid admin login
        good_login = await client.post("/api/v1/admin/login", json={
            "email": "admin@tax2biz.in",
            "password": "Tax2Biz@2026!"
        })
        assert good_login.status_code == 200
        assert "token" in good_login.json()

        # 3. Fetch KPI stats
        stats_resp = await client.get("/api/v1/admin/stats")
        assert stats_resp.status_code == 200
        stats = stats_resp.json()["stats"]
        assert "total_leads" in stats
        assert "total_revenue" in stats

        # 4. Create a lead to test updating
        lead_resp = await client.post("/api/v1/leads", json={
            "name": "Pooja Hegde",
            "email": "pooja@hegde.com",
            "phone": "9123456789",
            "company_name": "Hegde Media Pvt Ltd"
        })
        lead_id = lead_resp.json()["id"]

        # 5. Superadmin reassigns CA and marks In Process
        update_resp = await client.patch(f"/api/v1/admin/leads/{lead_id}", json={
            "status": "IN_PROCESS",
            "assigned_ca_name": "CA Priya Sharma",
            "assigned_ca_phone": "+91 98765 43211"
        })
        assert update_resp.status_code == 200
        assert update_resp.json()["lead"]["assigned_ca_name"] == "CA Priya Sharma"
        assert update_resp.json()["lead"]["status"] == "IN_PROCESS"

        # 6. Test CSV Export
        csv_resp = await client.get("/api/v1/admin/export-csv")
        assert csv_resp.status_code == 200
        assert "text/csv" in csv_resp.headers["content-type"]
        assert "Pooja Hegde" in csv_resp.text
