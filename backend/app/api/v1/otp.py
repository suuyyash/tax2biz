import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.app.core.database import get_db
from backend.app.core.security import (
    check_otp_rate_limit,
    generate_secure_otp,
    hash_otp,
    mask_phone
)
from backend.app.models.lead import OTPVerification, Lead
from backend.app.schemas.lead import OTPRequestSchema, OTPVerifySchema
from backend.app.providers.factory import get_notification_provider

router = APIRouter(prefix="/otp", tags=["OTP Verification"])

@router.post("/request")
async def request_otp(payload: OTPRequestSchema, db: AsyncSession = Depends(get_db)):
    """
    Generates and dispatches a secure 6-digit OTP to the founder's phone number.
    Protected by a sliding-window rate limiter (maximum 3 requests per 10 minutes).
    """
    allowed, retry_after = check_otp_rate_limit(payload.phone)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many OTP requests. Please wait {retry_after} seconds before requesting again."
        )

    # Invalidate previous unverified OTPs for this phone
    stmt = select(OTPVerification).where(
        (OTPVerification.phone == payload.phone) & (OTPVerification.is_verified == False)
    )
    res = await db.execute(stmt)
    old_records = res.scalars().all()
    for rec in old_records:
        rec.expires_at = datetime.utcnow() # Expire immediately

    # Generate new secure 6-digit OTP
    otp_code = generate_secure_otp(6)
    salt = secrets.token_hex(16)
    otp_hashed = hash_otp(otp_code, salt)
    expires = datetime.utcnow() + timedelta(minutes=10)

    otp_record = OTPVerification(
        phone=payload.phone,
        otp_hash=otp_hashed,
        salt=salt,
        expires_at=expires,
        attempts=0,
        is_verified=False
    )
    db.add(otp_record)
    await db.commit()

    # Dispatch via notification provider (logs to console in demo mode)
    notifier = get_notification_provider()
    await notifier.send_otp(payload.phone, otp_code)

    return {
        "status": "success",
        "message": f"Verification code sent to {mask_phone(payload.phone)}",
        "expiresInSeconds": 600,
        # In DEMO mode, we provide the code in the response for seamless testing without SMS delay
        "demoOtp": otp_code
    }


@router.post("/verify")
async def verify_otp(payload: OTPVerifySchema, db: AsyncSession = Depends(get_db)):
    """
    Verifies the submitted OTP against the salted hash with max attempts enforcement.
    """
    now = datetime.utcnow()
    stmt = (
        select(OTPVerification)
        .where(
            (OTPVerification.phone == payload.phone) &
            (OTPVerification.is_verified == False) &
            (OTPVerification.expires_at > now)
        )
        .order_by(desc(OTPVerification.created_at))
    )
    result = await db.execute(stmt)
    otp_record = result.scalars().first()

    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired or not found. Please request a new code."
        )

    if otp_record.attempts >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Maximum verification attempts exceeded. Please request a new OTP."
        )

    otp_record.attempts += 1
    computed_hash = hash_otp(payload.otp.strip(), otp_record.salt)

    if computed_hash != otp_record.otp_hash:
        await db.commit()
        remaining = 5 - otp_record.attempts
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid verification code. {remaining} attempts remaining."
        )

    # Success: Mark OTP verified
    otp_record.is_verified = True

    # If lead_id was provided, update lead status
    if payload.lead_id:
        lead_stmt = select(Lead).where(Lead.id == payload.lead_id)
        lead_res = await db.execute(lead_stmt)
        lead = lead_res.scalars().first()
        if lead:
            lead.status = "OTP_VERIFIED"

    await db.commit()

    return {
        "status": "success",
        "message": "Phone number verified successfully!",
        "phone": payload.phone,
        "verified": True
    }
