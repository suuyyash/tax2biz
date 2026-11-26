import logging
from typing import Tuple
from backend.app.providers.base import NotificationProviderInterface
from backend.app.core.security import mask_phone, mask_email

logger = logging.getLogger("tax2biz.notification.demo")

class MockNotificationProvider(NotificationProviderInterface):
    """
    Demo SMS & WhatsApp Provider.
    Logs simulated delivery clearly to console so developer/founder can test OTP and confirmations
    without incurring SMS charges or needing a live gateway account.
    """

    async def send_otp(self, phone: str, otp: str) -> Tuple[bool, str]:
        masked = mask_phone(phone)
        message = (
            f"[DEMO SMS / WhatsApp] 🚀 Tax2Biz Verification: Your OTP is {otp}. "
            f"Valid for 10 minutes. Do not share this code with anyone."
        )
        # Log visibly to terminal for easy testing
        print("\n" + "="*60)
        print(f"📲 NOTIFICATION SENT TO {masked}")
        print(message)
        print("="*60 + "\n")
        logger.info(f"Simulated OTP dispatch to {masked}")
        return True, "DEMO_MSG_ID_OK"

    async def send_booking_confirmation(
        self, phone: str, email: str, founder_name: str, ca_name: str, order_id: str
    ) -> bool:
        masked_p = mask_phone(phone)
        masked_e = mask_email(email)
        message = (
            f"[DEMO WhatsApp & Email] 🎉 Congratulations {founder_name}! Your Private Limited Registration "
            f"has been confirmed (Order #{order_id}). Senior Chartered Accountant {ca_name} has been assigned "
            f"and will reach out on {masked_p} within 15 minutes."
        )
        print("\n" + "*"*65)
        print(f"🧾 ORDER CONFIRMATION SENT TO {masked_p} & {masked_e}")
        print(message)
        print("*"*65 + "\n")
        logger.info(f"Simulated booking confirmation dispatch to {masked_p}")
        return True
