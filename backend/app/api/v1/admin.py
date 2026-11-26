import os
import io
import csv
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.lead import Lead
from backend.app.models.payment import Order, PaymentTransaction

logger = logging.getLogger("tax2biz.api.admin")
router = APIRouter(prefix="/admin", tags=["Superadmin"])

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

class AdminUpdateLeadRequest(BaseModel):
    status: Optional[str] = None
    assigned_ca_name: Optional[str] = None
    assigned_ca_phone: Optional[str] = None
    assigned_ca_cop: Optional[str] = None
    notes: Optional[str] = None

# Default Superadmin credentials (can be overridden via environment variables)
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@tax2biz.in")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Tax2Biz@2026!")

@router.post("/login")
async def admin_login(payload: AdminLoginRequest):
    """Authenticates the superadmin and returns an access session."""
    if payload.email.lower().strip() == ADMIN_EMAIL.lower() and payload.password == ADMIN_PASSWORD:
        return {
            "status": "success",
            "message": "Welcome back, Superadmin!",
            "admin": {
                "name": "Super Admin",
                "email": payload.email,
                "role": "SUPERADMIN"
            },
            "token": "t2b_adm_session_" + datetime.utcnow().strftime("%Y%m%d%H%M%S")
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid administrator credentials. Please check your email and password."
    )

@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Computes real-time KPI metrics for the superadmin dashboard."""
    # Total Leads
    total_res = await db.execute(select(func.count(Lead.id)))
    total_leads = total_res.scalar() or 0

    # Verified Leads (OTP verified or beyond)
    verified_res = await db.execute(
        select(func.count(Lead.id)).where(Lead.status.in_(["OTP_VERIFIED", "PLAN_SELECTED", "PAYMENT_PENDING", "PAID", "ASSIGNED_TO_CA", "IN_PROCESS", "INCORPORATED"]))
    )
    verified_leads = verified_res.scalar() or 0

    # Paid Leads
    paid_res = await db.execute(
        select(func.count(Lead.id)).where(Lead.status.in_(["PAID", "ASSIGNED_TO_CA", "IN_PROCESS", "INCORPORATED"]))
    )
    paid_customers = paid_res.scalar() or 0

    # Total Revenue in INR
    revenue_res = await db.execute(
        select(func.sum(Lead.amount)).where(Lead.status.in_(["PAID", "ASSIGNED_TO_CA", "IN_PROCESS", "INCORPORATED"]))
    )
    total_revenue = revenue_res.scalar() or 0

    return {
        "status": "success",
        "stats": {
            "total_leads": total_leads,
            "verified_leads": verified_leads,
            "paid_customers": paid_customers,
            "total_revenue": total_revenue
        }
    }

@router.patch("/leads/{lead_id}")
async def admin_update_lead(
    lead_id: str,
    payload: AdminUpdateLeadRequest,
    db: AsyncSession = Depends(get_db)
):
    """Allows superadmin to reassign Chartered Accountants or update funnel status."""
    stmt = select(Lead).where(Lead.id == lead_id)
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if payload.status:
        lead.status = payload.status
    if payload.assigned_ca_name:
        lead.assigned_ca_name = payload.assigned_ca_name
    if payload.assigned_ca_phone:
        lead.assigned_ca_phone = payload.assigned_ca_phone
    if payload.assigned_ca_cop:
        lead.assigned_ca_cop = payload.assigned_ca_cop
    if payload.notes is not None:
        lead.notes = payload.notes

    await db.commit()
    await db.refresh(lead)
    logger.info(f"Superadmin updated lead {lead.id} -> Status: {lead.status}, CA: {lead.assigned_ca_name}")
    return {
        "status": "success",
        "message": f"Lead #{lead.id} updated successfully",
        "lead": {
            "id": lead.id,
            "name": lead.name,
            "status": lead.status,
            "assigned_ca_name": lead.assigned_ca_name,
            "assigned_ca_phone": lead.assigned_ca_phone
        }
    }

@router.get("/export-csv")
async def export_leads_csv(db: AsyncSession = Depends(get_db)):
    """Exports all leads into a downloadable CSV file for Excel / Google Sheets."""
    stmt = select(Lead).order_by(desc(Lead.created_at))
    res = await db.execute(stmt)
    leads = res.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Lead ID", "Founder Name", "Email", "Phone", "State", 
        "Company Name", "Service", "Package", "Amount (INR)", 
        "Status", "Assigned CA", "Payment ID", "Created At"
    ])

    for l in leads:
        writer.writerow([
            l.id, l.name, l.email, l.phone, l.state or "",
            l.company_name or "", l.service, l.package, l.amount,
            l.status, l.assigned_ca_name or "", l.payment_id or "",
            l.created_at.strftime("%Y-%m-%d %H:%M:%S") if l.created_at else ""
        ])

    output.seek(0)
    filename = f"tax2biz_leads_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
