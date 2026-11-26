import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin

class Order(Base, TimestampMixin):
    """
    Payment Order representation (mirrors Razorpay / Cashfree order object).
    Enforces server-side amount calculation to prevent client tampering.
    """
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"ORD-{uuid.uuid4().hex[:12].upper()}")
    lead_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    gateway_order_id: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False) # In Rupees or paise
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    
    # Order Status: CREATED, ATTEMPTED, PAID, FAILED, REFUNDED
    status: Mapped[str] = mapped_column(String(30), default="CREATED", index=True)

    package_name: Mapped[str] = mapped_column(String(50), nullable=False)
    payment_mode: Mapped[str] = mapped_column(String(20), default="DEMO") # DEMO or RAZORPAY


class PaymentTransaction(Base, TimestampMixin):
    """
    Audited payment transaction log recorded upon webhook verification or successful checkout.
    """
    __tablename__ = "payment_transactions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"TXN-{uuid.uuid4().hex[:12].upper()}")
    order_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    gateway_payment_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    method: Mapped[str] = mapped_column(String(50), default="UPI")
    status: Mapped[str] = mapped_column(String(30), default="SUCCESS")
    
    # Raw webhook / response payload preserved for reconciliation
    raw_payload: Mapped[str] = mapped_column(Text, nullable=True)
