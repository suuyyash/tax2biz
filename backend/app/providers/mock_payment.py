import uuid
import hmac
import hashlib
import logging
from typing import Dict, Any
from backend.app.providers.base import PaymentGatewayInterface

logger = logging.getLogger("tax2biz.payment.demo")

class MockPaymentGateway(PaymentGatewayInterface):
    """
    Demo Payment Gateway that safely simulates full payment lifecycle without charging real money.
    Generates verifiable mock signatures and deterministic payment IDs.
    """
    DEMO_SECRET = "demo_webhook_secret_tax2biz_2026"

    async def create_order(self, amount: int, currency: str, receipt: str, notes: Dict[str, Any]) -> Dict[str, Any]:
        gateway_order_id = f"order_demo_{uuid.uuid4().hex[:14]}"
        logger.info(f"[DEMO GATEWAY] Created mock order {gateway_order_id} for amount ₹{amount} (Receipt: {receipt})")
        return {
            "id": gateway_order_id,
            "entity": "order",
            "amount": amount * 100, # In paise like Razorpay
            "amount_paid": 0,
            "currency": currency,
            "receipt": receipt,
            "status": "created",
            "notes": notes,
            "mode": "DEMO"
        }

    def verify_payment_signature(self, order_id: str, payment_id: str, signature: str) -> bool:
        """
        Verifies signature using HMAC-SHA256.
        In DEMO mode, signatures matching either the valid HMAC or 'demo_signature' are accepted.
        """
        if signature == "demo_signature" or signature.startswith("sig_demo_"):
            return True
            
        payload = f"{order_id}|{payment_id}".encode("utf-8")
        expected_signature = hmac.new(
            self.DEMO_SECRET.encode("utf-8"),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_signature, signature)

    def generate_demo_signature(self, order_id: str, payment_id: str) -> str:
        payload = f"{order_id}|{payment_id}".encode("utf-8")
        return hmac.new(
            self.DEMO_SECRET.encode("utf-8"),
            payload,
            hashlib.sha256
        ).hexdigest()
