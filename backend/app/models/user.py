import uuid
from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin

class Employee(Base, TimestampMixin):
    """
    Staff and Professional team members (Superadmin, CAs, Sales Executives, Compliance Managers).
    """
    __tablename__ = "employees"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"EMP-{uuid.uuid4().hex[:8].upper()}")
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="SENIOR_CA") # SUPERADMIN, SENIOR_CA, JUNIOR_CA, SALES_EXECUTIVE, COMPLIANCE_MANAGER
    cop_number: Mapped[str] = mapped_column(String(50), nullable=True) # Certificate of Practice (e.g. FCA #408912)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    leads_assigned_count: Mapped[int] = mapped_column(Integer, default=0)
