import uuid
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin

class LeadRemark(Base, TimestampMixin):
    """
    Audited followup history and activity timeline for each customer inquiry.
    Tracks calls, WhatsApp messages, status changes, assignments, notes, and document uploads.
    """
    __tablename__ = "lead_remarks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"REM-{uuid.uuid4().hex[:10].upper()}")
    lead_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    author_name: Mapped[str] = mapped_column(String(120), nullable=False)
    author_role: Mapped[str] = mapped_column(String(50), default="STAFF")
    remark_type: Mapped[str] = mapped_column(String(30), default="NOTE")
    # NOTE, CALL, WHATSAPP, STATUS_CHANGE, PRICE_UPDATE, ASSIGNMENT, DOC_UPDATE, EMAIL, ESCALATION
    content: Mapped[str] = mapped_column(Text, nullable=False)
