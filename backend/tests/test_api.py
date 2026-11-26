import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    await init_db()

@pytest.mark.asyncio
async def test_lead_creation_and_validation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Reject invalid phone number
        invalid_resp = await client.post("/api/v1/leads", json={
            "name": "Rohan Sharma",
            "email": "rohan@example.com",
            "phone": "12345", # Invalid Indian phone
            "company_name": "Sharma Tech Pvt Ltd"
        })
        assert invalid_resp.status_code == 422 # Pydantic Validation Error

        # 2. Accept valid lead
        valid_resp = await client.post("/api/v1/leads", json={
            "name": "Rohan Sharma",
            "email": "rohan@example.com",
            "phone": "9876543210",
            "state": "Maharashtra",
            "company_name": "Sharma Tech Pvt Ltd",
            "package": "Standard",
            "amount": 2499
        })
        assert valid_resp.status_code == 201
        data = valid_resp.json()
        assert data["name"] == "Rohan Sharma"
        assert data["assigned_ca_name"] == "CA Aakash Mehra"
        assert data["status"] == "NEW_INQUIRY"
        lead_id = data["id"]

        # 3. Request OTP
        otp_req_resp = await client.post("/api/v1/otp/request", json={
            "phone": "9876543210"
        })
        assert otp_req_resp.status_code == 200
        otp_data = otp_req_resp.json()
        demo_otp = otp_data.get("demoOtp")
        assert demo_otp is not None

        # 4. Verify OTP
        otp_verify_resp = await client.post("/api/v1/otp/verify", json={
            "phone": "9876543210",
            "otp": demo_otp,
            "lead_id": lead_id
        })
        assert otp_verify_resp.status_code == 200
        assert otp_verify_resp.json()["verified"] is True

        # 5. Create payment order
        order_resp = await client.post("/api/v1/payments/create-order", json={
            "lead_id": lead_id,
            "package_name": "Standard",
            "amount": 2499
        })
        assert order_resp.status_code == 200
        order_data = order_resp.json()
        order_id = order_data["order_id"]

        # 6. Process mock payment checkout
        checkout_resp = await client.post("/api/v1/payments/mock-checkout-submit", json={
            "order_id": order_id,
            "lead_id": lead_id,
            "method": "UPI",
            "upi_id": "rohan@oksbi"
        })
        assert checkout_resp.status_code == 200
        checkout_data = checkout_resp.json()
        assert checkout_data["status"] == "success"
        assert checkout_data["assignedCa"]["name"] == "CA Aakash Mehra"
