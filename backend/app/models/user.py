import uuid
from sqlalchemy import String, Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin

class Employee(Base, TimestampMixin):
    """
    Staff and Professional team members (Superadmin, CAs, Sales Executives, Compliance Managers).
    Stores plaintext password for Superadmin visibility (demo mode).
    In production, replace with bcrypt hash.
    """
    __tablename__ = "employees"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"EMP-{uuid.uuid4().hex[:8].upper()}")
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # Plaintext password stored for Superadmin visibility panel (demo mode only)
    password_plain: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="SENIOR_CA")
    # SUPERADMIN, SENIOR_CA, JUNIOR_CA, SALES_EXECUTIVE, COMPLIANCE_MANAGER
    cop_number: Mapped[str] = mapped_column(String(50), nullable=True)  # Certificate of Practice
    department: Mapped[str] = mapped_column(String(80), nullable=True, default="General")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    leads_assigned_count: Mapped[int] = mapped_column(Integer, default=0)
    avatar_color: Mapped[str] = mapped_column(String(10), nullable=True, default="#059669")
