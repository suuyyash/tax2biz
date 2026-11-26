from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class PaymentGatewayInterface(ABC):
    """Abstract interface defining required payment gateway operations."""

    @abstractmethod
    async def create_order(self, amount: int, currency: str, receipt: str, notes: Dict[str, Any]) -> Dict[str, Any]:
        """Create a gateway payment order."""
        pass

    @abstractmethod
    def verify_payment_signature(self, order_id: str, payment_id: str, signature: str) -> bool:
        """Verify HMAC payment signature from the gateway callback/webhook."""
        pass


class NotificationProviderInterface(ABC):
    """Abstract interface for multi-channel SMS and WhatsApp notifications."""

    @abstractmethod
    async def send_otp(self, phone: str, otp: str) -> Tuple[bool, str]:
        """Dispatch a one-time verification code."""
        pass

    @abstractmethod
    async def send_booking_confirmation(self, phone: str, email: str, founder_name: str, ca_name: str, order_id: str) -> bool:
        """Dispatch instant CA assignment & payment confirmation."""
        pass
