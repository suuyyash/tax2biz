from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class OrderCreateSchema(BaseModel):
    lead_id: str
    package_name: str = Field(..., description="Selected incorporation package")
    amount: int = Field(..., ge=1999, description="Professional fee in INR")

class OrderOutSchema(BaseModel):
    order_id: str
    lead_id: str
    amount: int
    currency: str = "INR"
    status: str
    gateway_order_id: Optional[str]
    payment_mode: str
    notes: Optional[Dict[str, Any]] = None

class MockPaymentSubmitSchema(BaseModel):
    order_id: str
    lead_id: str
    method: str = Field("UPI", pattern="^(UPI|Cards|Netbanking|Wallets)$")
    upi_id: Optional[str] = None

class PaymentVerificationSchema(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
