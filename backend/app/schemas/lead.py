import re
from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

class LeadCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=120, description="Founder's full legal name")
    email: EmailStr = Field(..., description="Official contact email")
    phone: str = Field(..., description="10-digit Indian mobile number")
    state: Optional[str] = Field(None, max_length=60, description="State of company incorporation")
    company_name: Optional[str] = Field(None, max_length=150, description="Proposed company name")
    service: Optional[str] = Field("Private Limited Company Registration", max_length=100)
    package: Optional[str] = Field("Standard", max_length=50)
    amount: Optional[int] = Field(2499, ge=0)

    @field_validator("phone")
    @classmethod
    def validate_indian_phone(cls, v: str) -> str:
        # Strip all spaces, dashes, +91 prefix
        cleaned = re.sub(r"[\s\-\+]", "", v)
        if cleaned.startswith("91") and len(cleaned) == 12:
            cleaned = cleaned[2:]
        if not re.match(r"^[6-9]\d{9}$", cleaned):
            raise ValueError("Invalid Indian mobile number. Must be a 10-digit number starting with 6, 7, 8, or 9.")
        return cleaned

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        clean = " ".join(v.split()).strip()
        if not re.match(r"^[a-zA-Z\s\.\']{2,120}$", clean):
            raise ValueError("Name can only contain alphabets, spaces, and periods.")
        return clean


class LeadUpdatePlanSchema(BaseModel):
    lead_id: str
    package: str = Field(..., pattern=r"^(Standard|Fast-Track SPICe\+|Complete Compliance)$")
    amount: int = Field(..., ge=1999)


class LeadOutSchema(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    state: Optional[str]
    company_name: Optional[str]
    service: str
    package: str
    amount: int
    status: str
    assigned_ca_name: Optional[str]
    assigned_ca_phone: Optional[str]
    assigned_ca_cop: Optional[str]
    payment_id: Optional[str] = None
    paid_at: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)


class OTPRequestSchema(BaseModel):
    phone: str = Field(..., description="10-digit mobile number to send OTP")

    @field_validator("phone")
    @classmethod
    def validate_indian_phone(cls, v: str) -> str:
        cleaned = re.sub(r"[\s\-\+]", "", v)
        if cleaned.startswith("91") and len(cleaned) == 12:
            cleaned = cleaned[2:]
        if not re.match(r"^[6-9]\d{9}$", cleaned):
            raise ValueError("Invalid Indian mobile number.")
        return cleaned


class OTPVerifySchema(BaseModel):
    phone: str
    otp: str = Field(..., min_length=4, max_length=6, pattern="^[0-9]{4,6}$")
    lead_id: Optional[str] = None
