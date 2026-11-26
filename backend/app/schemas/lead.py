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
    state: Optional[str] = None
    city: Optional[str] = None
    company_name: Optional[str] = None
    service: str
    service_item: Optional[str] = None
    company_turnover: Optional[str] = None
    authorized_capital: Optional[str] = None
    agreed_price: Optional[int] = None
    priority: Optional[str] = "MEDIUM"
    package: str
    amount: int
    status: str
    assigned_to_id: Optional[str] = None
    assigned_ca_name: Optional[str] = None
    assigned_ca_phone: Optional[str] = None
    assigned_ca_cop: Optional[str] = None
    payment_id: Optional[str] = None
    payment_method: Optional[str] = None
    paid_at: Optional[Any] = None
    source: Optional[str] = None
    # Document checklist
    docs_pan: Optional[bool] = False
    docs_aadhaar: Optional[bool] = False
    docs_photo: Optional[bool] = False
    docs_address_proof: Optional[bool] = False
    docs_dsc: Optional[bool] = False
    docs_moa_aoa: Optional[bool] = False
    created_at: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)


class ManualLeadCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    phone: str
    service: str = Field(..., description="Service category")
    service_item: str = Field(..., description="Specific sub-service")
    company_name: Optional[str] = None
    state: Optional[str] = None
    company_turnover: Optional[str] = "< ₹20 Lakhs"
    authorized_capital: Optional[str] = "₹1,00,000"
    priority: Optional[str] = "MEDIUM"
    package: Optional[str] = "Standard"
    amount: Optional[int] = 2499
    assigned_ca_name: Optional[str] = "CA Aakash Mehra"
    initial_remark: Optional[str] = None


class LeadRemarkCreateSchema(BaseModel):
    content: str = Field(..., min_length=2, max_length=1000)
    remark_type: Optional[str] = "NOTE"  # NOTE, CALL, WHATSAPP, STATUS_CHANGE, PRICE_UPDATE, ASSIGNMENT
    author_name: Optional[str] = "Staff"
    author_role: Optional[str] = "CA"


class LeadConvertSchema(BaseModel):
    agreed_price: int = Field(..., ge=0, description="Final agreed conversion price in INR")
    payment_method: str = Field("UPI", description="UPI, Bank Transfer, Cash, or Payment Link")
    payment_id: Optional[str] = None
    notes: Optional[str] = None


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
