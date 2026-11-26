import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin

class Lead(Base, TimestampMixin):
    """
    Core Lead model tracking the user through the incorporation/filing funnel.
    """
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"LEAD-{uuid.uuid4().hex[:10].upper()}")
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(60), nullable=True)
    company_name: Mapped[str] = mapped_column(String(150), nullable=True)
    service: Mapped[str] = mapped_column(String(100), default="Business Registration")
    service_item: Mapped[str] = mapped_column(String(150), default="Private Limited Company Registration")
    
    # Financial & Business Metrics
    company_turnover: Mapped[str] = mapped_column(String(60), nullable=True, default="< ₹20 Lakhs")
    authorized_capital: Mapped[str] = mapped_column(String(60), nullable=True, default="₹1,00,000")
    priority: Mapped[str] = mapped_column(String(20), default="MEDIUM") # HIGH, MEDIUM, LOW
    
    # Selected plan details
    package: Mapped[str] = mapped_column(String(50), default="Standard")
    amount: Mapped[int] = mapped_column(Integer, default=2499)
    agreed_price: Mapped[int] = mapped_column(Integer, nullable=True) # Final closing/converted price
    govt_fees_estimated: Mapped[int] = mapped_column(Integer, default=1000)

    # Funnel status: NEW_INQUIRY, OTP_VERIFIED, PLAN_SELECTED, PAYMENT_PENDING, PAID, IN_PROCESS, INCORPORATED, LOST
    status: Mapped[str] = mapped_column(String(40), default="NEW_INQUIRY", index=True)

    # Assigned Staff / Chartered Accountant
    assigned_to_id: Mapped[str] = mapped_column(String(64), nullable=True)
    assigned_ca_name: Mapped[str] = mapped_column(String(100), nullable=True, default="CA Aakash Mehra")
    assigned_ca_phone: Mapped[str] = mapped_column(String(20), nullable=True, default="+91 98765 43210")
    assigned_ca_cop: Mapped[str] = mapped_column(String(50), nullable=True, default="FCA #408912")
    next_followup_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Payment link reference
    payment_id: Mapped[str] = mapped_column(String(100), nullable=True)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=True)
    paid_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    source: Mapped[str] = mapped_column(String(50), default="landing_page_form")
    notes: Mapped[str] = mapped_column(Text, nullable=True)


class OTPVerification(Base, TimestampMixin):
    """
    Records OTP sessions with cryptographic salting, expiration, and attempt limits.
    """
    __tablename__ = "otp_verifications"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: uuid.uuid4().hex)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    otp_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    salt: Mapped[str] = mapped_column(String(32), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
