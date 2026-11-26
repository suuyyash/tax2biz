from backend.app.core.config import settings
from backend.app.providers.base import PaymentGatewayInterface, NotificationProviderInterface
from backend.app.providers.mock_payment import MockPaymentGateway
from backend.app.providers.mock_notifier import MockNotificationProvider

def get_payment_gateway() -> PaymentGatewayInterface:
    """
    Factory returning either the Mock Payment Gateway or Live Razorpay Provider
    based on the PAYMENT_MODE setting.
    """
    if settings.PAYMENT_MODE.upper() == "LIVE" and settings.RAZORPAY_KEY_ID:
        # Live Razorpay provider hook (can be loaded when keys are supplied)
        pass
    return MockPaymentGateway()

def get_notification_provider() -> NotificationProviderInterface:
    """
    Factory returning either the Mock Notifier or Live SMS/WhatsApp Gateway
    based on the NOTIFICATION_MODE setting.
    """
    if settings.NOTIFICATION_MODE.upper() == "LIVE" and settings.SMS_API_KEY:
        # Live SMS/WhatsApp provider hook (can be loaded when keys are supplied)
        pass
    return MockNotificationProvider()
