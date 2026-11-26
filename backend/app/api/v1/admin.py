import os
import io
import csv
import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, asc, or_
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.core.security import hash_otp
from backend.app.models.lead import Lead
from backend.app.models.user import Employee
from backend.app.models.remark import LeadRemark
from backend.app.models.payment import Order, PaymentTransaction
from backend.app.schemas.lead import (
    ManualLeadCreateSchema,
    LeadRemarkCreateSchema,
    LeadConvertSchema,
    LeadOutSchema
)

logger = logging.getLogger("tax2biz.api.admin")
router = APIRouter(prefix="/admin", tags=["Superadmin"])

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@tax2biz.in")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Tax2Biz@2026!")

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

class EmployeeCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone: Optional[str] = "+91 98765 43210"
    role: str = Field("SENIOR_CA", description="SUPERADMIN, SENIOR_CA, JUNIOR_CA, SALES_EXECUTIVE, COMPLIANCE_MANAGER")
    cop_number: Optional[str] = "FCA #408912"
    department: Optional[str] = "General"

class EmployeeOutSchema(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    role: str
    cop_number: Optional[str]
    department: Optional[str] = "General"
    is_active: bool
    leads_assigned_count: int
    password_plain: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AdminUpdateLeadRequest(BaseModel):
    status: Optional[str] = None
    service: Optional[str] = None
    service_item: Optional[str] = None
    company_turnover: Optional[str] = None
    agreed_price: Optional[int] = None
    priority: Optional[str] = None
    assigned_ca_name: Optional[str] = None
    assigned_ca_phone: Optional[str] = None
    assigned_ca_cop: Optional[str] = None
    assigned_to_id: Optional[str] = None
    notes: Optional[str] = None
    next_followup_date: Optional[str] = None
    # Document checklist updates
    docs_pan: Optional[bool] = None
    docs_aadhaar: Optional[bool] = None
    docs_photo: Optional[bool] = None
    docs_address_proof: Optional[bool] = None
    docs_dsc: Optional[bool] = None
    docs_moa_aoa: Optional[bool] = None


# ─────────────────────────────────────────────────────────────
# 1. AUTHENTICATION & EMPLOYEE MANAGEMENT
# ─────────────────────────────────────────────────────────────
@router.post("/login")
async def admin_or_employee_login(payload: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Unified login supporting Superadmin and Role-based Employee/Staff logins.
    """
    clean_email = payload.email.lower().strip()
    
    # 1. Check Root Superadmin credentials
    if clean_email == ADMIN_EMAIL.lower() and payload.password == ADMIN_PASSWORD:
        return {
            "status": "success",
            "message": "Welcome back, Superadmin!",
            "user": {
                "id": "EMP-ROOT-SUPERADMIN",
                "name": "Super Admin",
                "email": clean_email,
                "role": "SUPERADMIN",
                "cop_number": "FCA Fellow CA"
            },
            "token": "t2b_adm_session_" + datetime.utcnow().strftime("%Y%m%d%H%M%S")
        }

    # 2. Check Employee database
    stmt = select(Employee).where((Employee.email == clean_email) & (Employee.is_active == True))
    res = await db.execute(stmt)
    emp = res.scalars().first()
    if emp and (emp.password_hash == payload.password or emp.password_plain == payload.password):
        return {
            "status": "success",
            "message": f"Welcome back, {emp.name}!",
            "user": {
                "id": emp.id,
                "name": emp.name,
                "email": emp.email,
                "role": emp.role,
                "phone": emp.phone,
                "cop_number": emp.cop_number
            },
            "token": f"t2b_emp_{emp.id}_" + datetime.utcnow().strftime("%Y%m%d%H%M%S")
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials. Please verify your official email and password."
    )


@router.post("/employees", response_model=EmployeeOutSchema)
async def create_employee(payload: EmployeeCreateSchema, db: AsyncSession = Depends(get_db)):
    """Creates a new CA or staff member account for role-based portal access."""
    stmt = select(Employee).where(Employee.email == payload.email.lower().strip())
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(status_code=400, detail="Employee with this email already exists.")

    emp = Employee(
        name=payload.name,
        email=payload.email.lower().strip(),
        password_hash=payload.password,
        password_plain=payload.password,  # Stored for Superadmin visibility
        phone=payload.phone,
        role=payload.role,
        cop_number=payload.cop_number,
        department=payload.department or "General",
        is_active=True,
        leads_assigned_count=0
    )
    db.add(emp)
    await db.commit()
    await db.refresh(emp)
    return emp


@router.get("/employees", response_model=List[EmployeeOutSchema])
async def list_employees(db: AsyncSession = Depends(get_db)):
    """Lists all active employees and CAs with their current lead loads."""
    stmt = select(Employee).order_by(asc(Employee.name))
    res = await db.execute(stmt)
    employees = res.scalars().all()
    
    # If no employees exist in DB yet, auto-seed default expert team for demo
    if not employees:
        defaults = [
            Employee(name="CA Aakash Mehra", email="aakash.ca@tax2biz.in", password_hash="Tax2Biz@2026!", password_plain="Tax2Biz@2026!", phone="+91 98765 43210", role="SENIOR_CA", cop_number="FCA #408912", department="Company Registration"),
            Employee(name="CA Priya Sharma", email="priya.ca@tax2biz.in", password_hash="Tax2Biz@2026!", password_plain="Tax2Biz@2026!", phone="+91 98765 43211", role="SENIOR_CA", cop_number="ACA #512398", department="Tax & Audit"),
            Employee(name="CS Rahul Verma", email="rahul.cs@tax2biz.in", password_hash="Tax2Biz@2026!", password_plain="Tax2Biz@2026!", phone="+91 98765 43212", role="COMPLIANCE_MANAGER", cop_number="FCS #10928", department="ROC Compliance"),
            Employee(name="Vikram Sethi", email="vikram.sales@tax2biz.in", password_hash="Tax2Biz@2026!", password_plain="Tax2Biz@2026!", phone="+91 98765 43213", role="SALES_EXECUTIVE", cop_number="Sales Lead", department="Sales"),
        ]
        db.add_all(defaults)
        await db.commit()
        res = await db.execute(stmt)
        employees = res.scalars().all()

    return employees


@router.patch("/employees/{emp_id}")
async def update_employee(emp_id: str, db: AsyncSession = Depends(get_db)):
    """Toggle employee active/inactive status."""
    stmt = select(Employee).where(Employee.id == emp_id)
    res = await db.execute(stmt)
    emp = res.scalars().first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp.is_active = not emp.is_active
    await db.commit()
    return {"status": "success", "is_active": emp.is_active}


@router.delete("/employees/{emp_id}")
async def delete_employee(emp_id: str, db: AsyncSession = Depends(get_db)):
    """Deactivates an employee (soft delete)."""
    stmt = select(Employee).where(Employee.id == emp_id)
    res = await db.execute(stmt)
    emp = res.scalars().first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp.is_active = False
    await db.commit()
    return {"status": "success", "message": f"{emp.name} deactivated"}


# ─────────────────────────────────────────────────────────────
# 2. MANUAL LEAD ENTRY & SERVICE MANAGEMENT
# ─────────────────────────────────────────────────────────────
@router.post("/leads/manual", response_model=LeadOutSchema)
async def create_manual_lead(payload: ManualLeadCreateSchema, db: AsyncSession = Depends(get_db)):
    """
    Manually creates an inquiry entry for walk-in or offline founders
    with complete company turnover, service selection, and initial remarks.
    """
    new_lead = Lead(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        state=payload.state,
        company_name=payload.company_name,
        service=payload.service,
        service_item=payload.service_item,
        company_turnover=payload.company_turnover or "< ₹20 Lakhs",
        authorized_capital=payload.authorized_capital or "₹1,00,000",
        priority=payload.priority or "MEDIUM",
        package=payload.package or "Standard",
        amount=payload.amount or 2499,
        status="NEW_INQUIRY",
        assigned_ca_name=payload.assigned_ca_name or "CA Aakash Mehra",
        source="manual_admin_entry"
    )
    db.add(new_lead)
    await db.flush()

    # Record initial remark if provided
    if payload.initial_remark:
        remark = LeadRemark(
            lead_id=new_lead.id,
            author_name="Superadmin",
            author_role="SUPERADMIN",
            remark_type="NOTE",
            content=payload.initial_remark
        )
        db.add(remark)

    await db.commit()
    await db.refresh(new_lead)
    return new_lead


# ─────────────────────────────────────────────────────────────
# 3. FOLLOWUP REMARKS & TIMELINE
# ─────────────────────────────────────────────────────────────
@router.post("/leads/{lead_id}/remarks")
async def add_lead_remark(
    lead_id: str,
    payload: LeadRemarkCreateSchema,
    db: AsyncSession = Depends(get_db)
):
    """Adds a call remark, follow-up note, or WhatsApp log to a lead."""
    stmt = select(Lead).where(Lead.id == lead_id)
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    remark = LeadRemark(
        lead_id=lead.id,
        author_name=payload.author_name or "Staff",
        author_role=payload.author_role or "CA",
        remark_type=payload.remark_type or "NOTE",
        content=payload.content
    )
    db.add(remark)
    await db.commit()
    await db.refresh(remark)
    return {
        "status": "success",
        "message": "Followup remark logged",
        "remark": {
            "id": remark.id,
            "lead_id": remark.lead_id,
            "author_name": remark.author_name,
            "author_role": remark.author_role,
            "remark_type": remark.remark_type,
            "content": remark.content,
            "created_at": remark.created_at.strftime("%d %b %Y, %I:%M %p")
        }
    }


@router.get("/leads/{lead_id}/remarks")
async def list_lead_remarks(lead_id: str, db: AsyncSession = Depends(get_db)):
    """Fetches the full activity and followup timeline for a lead."""
    stmt = select(LeadRemark).where(LeadRemark.lead_id == lead_id).order_by(desc(LeadRemark.created_at))
    res = await db.execute(stmt)
    remarks = res.scalars().all()
    return {
        "status": "success",
        "lead_id": lead_id,
        "count": len(remarks),
        "remarks": [
            {
                "id": r.id,
                "author_name": r.author_name,
                "author_role": r.author_role,
                "remark_type": r.remark_type,
                "content": r.content,
                "created_at": r.created_at.strftime("%d %b %Y, %I:%M %p") if r.created_at else ""
            }
            for r in remarks
        ]
    }


# ─────────────────────────────────────────────────────────────
# 4. CONVERT LEAD WITH CUSTOM AGREED PRICE
# ─────────────────────────────────────────────────────────────
@router.post("/leads/{lead_id}/convert")
async def convert_lead_with_price(
    lead_id: str,
    payload: LeadConvertSchema,
    db: AsyncSession = Depends(get_db)
):
    """
    Marks a lead as converted with the agreed professional fee and payment details.
    """
    stmt = select(Lead).where(Lead.id == lead_id)
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    payment_id = payload.payment_id or f"PAY-OFFLINE-{uuid.uuid4().hex[:8].upper()}"
    lead.status = "PAID"
    lead.agreed_price = payload.agreed_price
    lead.amount = payload.agreed_price
    lead.payment_id = payment_id
    lead.payment_method = payload.payment_method
    lead.paid_at = datetime.utcnow()

    # Log conversion remark
    remark = LeadRemark(
        lead_id=lead.id,
        author_name="Superadmin",
        author_role="SUPERADMIN",
        remark_type="PRICE_UPDATE",
        content=f"🎉 Deal converted! Agreed professional fee: ₹{payload.agreed_price:,} via {payload.payment_method}. (Ref: {payment_id})"
    )
    db.add(remark)

    await db.commit()
    await db.refresh(lead)
    return {
        "status": "success",
        "message": f"Lead converted successfully at agreed price ₹{payload.agreed_price:,}!",
        "lead_id": lead.id,
        "agreed_price": lead.agreed_price,
        "payment_id": lead.payment_id
    }


# ─────────────────────────────────────────────────────────────
# 5. AUTO-ASSIGNMENT ENGINE
# ─────────────────────────────────────────────────────────────
@router.post("/leads/{lead_id}/auto-assign")
async def auto_assign_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    """
    Intelligently assigns the lead to the active CA/Employee with the lowest current workload (Round-Robin).
    """
    stmt = select(Lead).where(Lead.id == lead_id)
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Fetch active employees
    emp_stmt = select(Employee).where(Employee.is_active == True).order_by(asc(Employee.leads_assigned_count))
    emp_res = await db.execute(emp_stmt)
    employees = emp_res.scalars().all()

    if not employees:
        # Default fallback
        lead.assigned_ca_name = "CA Aakash Mehra"
        lead.assigned_ca_phone = "+91 98765 43210"
        assigned_emp_name = "CA Aakash Mehra"
    else:
        best_emp = employees[0]  # Lowest workload
        lead.assigned_to_id = best_emp.id
        lead.assigned_ca_name = best_emp.name
        lead.assigned_ca_phone = best_emp.phone or "+91 98765 43210"
        lead.assigned_ca_cop = best_emp.cop_number or "FCA Registered"
        best_emp.leads_assigned_count += 1
        assigned_emp_name = best_emp.name

    remark = LeadRemark(
        lead_id=lead.id,
        author_name="Auto-Assign Engine",
        author_role="SYSTEM",
        remark_type="ASSIGNMENT",
        content=f"System auto-assigned lead to {assigned_emp_name} based on current team workload."
    )
    db.add(remark)
    await db.commit()
    await db.refresh(lead)

    return {
        "status": "success",
        "message": f"Lead auto-assigned to {assigned_emp_name}",
        "assigned_to": assigned_emp_name,
        "lead_id": lead.id
    }


# ─────────────────────────────────────────────────────────────
# 6. DASHBOARD METRICS & TURNOVER BREAKDOWN
# ─────────────────────────────────────────────────────────────
@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Computes real-time KPI metrics, service volume, and revenue totals."""
    total_res = await db.execute(select(func.count(Lead.id)))
    total_leads = total_res.scalar() or 0

    verified_res = await db.execute(
        select(func.count(Lead.id)).where(Lead.status.in_(["OTP_VERIFIED", "PLAN_SELECTED", "PAYMENT_PENDING", "PAID", "IN_PROCESS", "INCORPORATED", "DOCS_PENDING", "DOCS_RECEIVED", "GOVT_FILING", "DELIVERED"]))
    )
    verified_leads = verified_res.scalar() or 0

    paid_res = await db.execute(
        select(func.count(Lead.id)).where(Lead.status.in_(["PAID", "IN_PROCESS", "INCORPORATED", "DOCS_PENDING", "DOCS_RECEIVED", "GOVT_FILING", "DELIVERED"]))
    )
    paid_customers = paid_res.scalar() or 0

    revenue_res = await db.execute(
        select(func.sum(Lead.amount)).where(Lead.status.in_(["PAID", "IN_PROCESS", "INCORPORATED", "DOCS_PENDING", "DOCS_RECEIVED", "GOVT_FILING", "DELIVERED"]))
    )
    total_revenue = revenue_res.scalar() or 0

    # Pipeline value (potential revenue from non-lost, non-paid leads)
    pipeline_res = await db.execute(
        select(func.sum(Lead.amount)).where(Lead.status.in_(["NEW_INQUIRY", "OTP_VERIFIED", "PLAN_SELECTED", "PAYMENT_PENDING"]))
    )
    pipeline_value = pipeline_res.scalar() or 0

    # Lost leads count
    lost_res = await db.execute(
        select(func.count(Lead.id)).where(Lead.status == "LOST")
    )
    lost_leads = lost_res.scalar() or 0

    # In-process (actively working)
    in_process_res = await db.execute(
        select(func.count(Lead.id)).where(Lead.status.in_(["IN_PROCESS", "DOCS_PENDING", "DOCS_RECEIVED", "GOVT_FILING"]))
    )
    in_process = in_process_res.scalar() or 0

    # Service Distribution breakdown
    service_counts = {}
    srv_stmt = select(Lead.service, func.count(Lead.id)).group_by(Lead.service)
    srv_res = await db.execute(srv_stmt)
    for row in srv_res.all():
        service_counts[row[0] or "General"] = row[1]

    # Turnover Distribution breakdown
    turnover_counts = {}
    to_stmt = select(Lead.company_turnover, func.count(Lead.id)).group_by(Lead.company_turnover)
    to_res = await db.execute(to_stmt)
    for row in to_res.all():
        turnover_counts[row[0] or "Unspecified"] = row[1]

    # Source distribution
    source_counts = {}
    src_stmt = select(Lead.source, func.count(Lead.id)).group_by(Lead.source)
    src_res = await db.execute(src_stmt)
    for row in src_res.all():
        source_counts[row[0] or "direct"] = row[1]

    # Status distribution
    status_counts = {}
    st_stmt = select(Lead.status, func.count(Lead.id)).group_by(Lead.status)
    st_res = await db.execute(st_stmt)
    for row in st_res.all():
        status_counts[row[0]] = row[1]

    # Employee workload
    emp_stmt = select(Employee.name, Employee.leads_assigned_count).where(Employee.is_active == True).order_by(desc(Employee.leads_assigned_count))
    emp_res = await db.execute(emp_stmt)
    employee_workload = {row[0]: row[1] for row in emp_res.all()}

    return {
        "status": "success",
        "stats": {
            "total_leads": total_leads,
            "verified_leads": verified_leads,
            "paid_customers": paid_customers,
            "total_revenue": total_revenue,
            "pipeline_value": pipeline_value,
            "lost_leads": lost_leads,
            "in_process": in_process,
            "service_counts": service_counts,
            "turnover_counts": turnover_counts,
            "source_counts": source_counts,
            "status_counts": status_counts,
            "employee_workload": employee_workload
        }
    }


@router.patch("/leads/{lead_id}")
async def admin_update_lead(
    lead_id: str,
    payload: AdminUpdateLeadRequest,
    db: AsyncSession = Depends(get_db)
):
    """Allows updating any field of a lead (status, priority, price, assigned CA, documents)."""
    stmt = select(Lead).where(Lead.id == lead_id)
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    changes = []
    if payload.status and payload.status != lead.status:
        changes.append(f"Status changed from {lead.status} to {payload.status}")
        lead.status = payload.status
    if payload.service:
        lead.service = payload.service
    if payload.service_item:
        lead.service_item = payload.service_item
    if payload.company_turnover:
        lead.company_turnover = payload.company_turnover
    if payload.agreed_price is not None:
        lead.agreed_price = payload.agreed_price
        lead.amount = payload.agreed_price
        changes.append(f"Agreed fee set to ₹{payload.agreed_price:,}")
    if payload.priority:
        lead.priority = payload.priority
    if payload.assigned_ca_name and payload.assigned_ca_name != lead.assigned_ca_name:
        changes.append(f"Reassigned to {payload.assigned_ca_name}")
        lead.assigned_ca_name = payload.assigned_ca_name
    if payload.assigned_ca_phone:
        lead.assigned_ca_phone = payload.assigned_ca_phone
    if payload.assigned_ca_cop:
        lead.assigned_ca_cop = payload.assigned_ca_cop
    if payload.assigned_to_id:
        lead.assigned_to_id = payload.assigned_to_id
    # Document checklist updates
    if payload.docs_pan is not None:
        lead.docs_pan = payload.docs_pan
    if payload.docs_aadhaar is not None:
        lead.docs_aadhaar = payload.docs_aadhaar
    if payload.docs_photo is not None:
        lead.docs_photo = payload.docs_photo
    if payload.docs_address_proof is not None:
        lead.docs_address_proof = payload.docs_address_proof
    if payload.docs_dsc is not None:
        lead.docs_dsc = payload.docs_dsc
    if payload.docs_moa_aoa is not None:
        lead.docs_moa_aoa = payload.docs_moa_aoa

    # Record audit log remark
    if changes:
        remark = LeadRemark(
            lead_id=lead.id,
            author_name="Superadmin",
            author_role="SUPERADMIN",
            remark_type="STATUS_CHANGE",
            content="; ".join(changes)
        )
        db.add(remark)

    await db.commit()
    await db.refresh(lead)
    return {
        "status": "success",
        "message": f"Lead #{lead.id} updated successfully",
        "lead": lead
    }


# ─────────────────────────────────────────────────────────────
# 7. EXPORT CSV FOR EXCEL & ACCOUNTING
# ─────────────────────────────────────────────────────────────
@router.get("/export-csv")
async def export_leads_csv(db: AsyncSession = Depends(get_db)):
    """Exports all leads into an Excel-ready CSV with turnover, service, and conversion data."""
    stmt = select(Lead).order_by(desc(Lead.created_at))
    res = await db.execute(stmt)
    leads = res.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Lead ID", "Founder Name", "Email", "Phone", "State", 
        "Company Name", "Service Category", "Sub-Service", 
        "Company Turnover", "Authorized Capital", "Priority", 
        "Package", "Amount (INR)", "Agreed Price", "Status", 
        "Assigned Professional", "Payment ID", "Source", "Received Date"
    ])

    for l in leads:
        writer.writerow([
            l.id, l.name, l.email, l.phone, l.state or "",
            l.company_name or "", l.service or "", l.service_item or "",
            l.company_turnover or "", l.authorized_capital or "", l.priority or "MEDIUM",
            l.package, l.amount, l.agreed_price or l.amount,
            l.status, l.assigned_ca_name or "", l.payment_id or "",
            l.source or "landing_page", 
            l.created_at.strftime("%Y-%m-%d %H:%M:%S") if l.created_at else ""
        ])

    output.seek(0)
    filename = f"tax2biz_enterprise_leads_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ─────────────────────────────────────────────────────────────
# 8. SEED DEMO DATA (for first-time setup)
# ─────────────────────────────────────────────────────────────
@router.post("/seed-demo")
async def seed_demo_data(db: AsyncSession = Depends(get_db)):
    """Seeds demo leads across all services for immediate testing."""
    total_res = await db.execute(select(func.count(Lead.id)))
    existing = total_res.scalar() or 0
    if existing > 0:
        return {"status": "info", "message": f"Database already has {existing} leads. Skipping seed."}

    demo_leads = [
        Lead(name="Rahul Sharma", email="rahul@acme.in", phone="9876543210", state="Maharashtra", company_name="Acme Innovations Pvt Ltd", service="Business Registration", service_item="Private Limited Company Registration", company_turnover="₹20L - ₹1 Crore", amount=2499, status="OTP_VERIFIED", source="landing_page_form", priority="HIGH"),
        Lead(name="Priya Patel", email="priya@greenleaf.in", phone="9876543211", state="Gujarat", company_name="GreenLeaf Organics LLP", service="Business Registration", service_item="LLP Registration", company_turnover="< ₹20 Lakhs", amount=3999, status="PAID", source="google_ads", priority="HIGH", agreed_price=3999),
        Lead(name="Arun Kumar", email="arun@techforge.in", phone="9876543212", state="Karnataka", company_name="TechForge Solutions", service="Tax & Audit", service_item="ITR-3 Business Filing", company_turnover="₹1 Cr - ₹5 Crore", amount=4999, status="NEW_INQUIRY", source="landing_page_form", priority="MEDIUM"),
        Lead(name="Sneha Joshi", email="sneha@craftcafe.in", phone="9876543213", state="Delhi", company_name="CraftCafe India Pvt Ltd", service="GST & Accounting", service_item="GST Registration", company_turnover="< ₹20 Lakhs", amount=1999, status="PLAN_SELECTED", source="whatsapp", priority="LOW"),
        Lead(name="Vikrant Singh", email="vikrant@shieldip.in", phone="9876543214", state="Rajasthan", company_name="ShieldIP Trademarks", service="Trademark", service_item="Trademark Application Filing", company_turnover="₹20L - ₹1 Crore", amount=6999, status="IN_PROCESS", source="phone_call", priority="HIGH"),
        Lead(name="Meera Reddy", email="meera@cloudnine.in", phone="9876543215", state="Telangana", company_name="CloudNine Infra Pvt Ltd", service="ROC Compliance", service_item="ROC Annual Compliance", company_turnover="₹1 Cr - ₹5 Crore", amount=5999, status="PAYMENT_PENDING", source="referral", priority="MEDIUM"),
        Lead(name="Deepak Verma", email="deepak@nova.in", phone="9876543216", state="Uttar Pradesh", company_name="Nova Enterprises", service="Business Registration", service_item="One Person Company (OPC)", company_turnover="< ₹20 Lakhs", amount=2999, status="LOST", source="google_ads", priority="LOW"),
        Lead(name="Anjali Deshmukh", email="anjali@spicetrail.in", phone="9876543217", state="Maharashtra", company_name="SpiceTrail Foods Pvt Ltd", service="GST & Accounting", service_item="Monthly GST Return Filing", company_turnover="₹5 Crore+", amount=7999, status="PAID", source="landing_page_form", priority="HIGH", agreed_price=7999),
    ]
    db.add_all(demo_leads)

    # Add remarks for some leads
    await db.flush()
    for lead in demo_leads[:3]:
        remark = LeadRemark(
            lead_id=lead.id,
            author_name="CA Aakash Mehra",
            author_role="SENIOR_CA",
            remark_type="CALL",
            content=f"Initial discovery call with {lead.name}. Discussed service requirements and pricing."
        )
        db.add(remark)

    await db.commit()
    return {"status": "success", "message": f"Seeded {len(demo_leads)} demo leads across all services."}
