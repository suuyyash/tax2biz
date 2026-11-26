import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.app.core.database import get_db
from backend.app.models.lead import Lead
from backend.app.schemas.lead import LeadCreateSchema, LeadUpdatePlanSchema, LeadOutSchema

logger = logging.getLogger("tax2biz.api.leads")
router = APIRouter(prefix="/leads", tags=["Leads"])

@router.post("", response_model=LeadOutSchema, status_code=status.HTTP_201_CREATED)
async def create_lead(payload: LeadCreateSchema, db: AsyncSession = Depends(get_db)):
    """
    Creates a new incorporation lead with strict validation.
    Assigns a default Chartered Accountant to the inquiry immediately.
    """
    # Check for existing lead with same phone or email to update or create
    stmt = select(Lead).where((Lead.phone == payload.phone) | (Lead.email == payload.email)).order_by(desc(Lead.created_at))
    result = await db.execute(stmt)
    existing_lead = result.scalars().first()

    if existing_lead and existing_lead.status != "PAID":
        # Update existing draft lead
        existing_lead.name = payload.name
        existing_lead.email = payload.email
        existing_lead.phone = payload.phone
        existing_lead.state = payload.state or existing_lead.state
        existing_lead.company_name = payload.company_name or existing_lead.company_name
        existing_lead.package = payload.package or existing_lead.package
        existing_lead.amount = payload.amount or existing_lead.amount
        await db.commit()
        await db.refresh(existing_lead)
        logger.info(f"Updated existing lead {existing_lead.id}")
        return existing_lead

    # Create new lead
    new_lead = Lead(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        state=payload.state,
        company_name=payload.company_name,
        service=payload.service or "Private Limited Company Registration",
        package=payload.package or "Standard",
        amount=payload.amount or 2499,
        status="NEW_INQUIRY",
        assigned_ca_name="CA Aakash Mehra",
        assigned_ca_phone="+91 98765 43210",
        assigned_ca_cop="FCA #408912"
    )
    db.add(new_lead)
    await db.commit()
    await db.refresh(new_lead)
    logger.info(f"Created new lead {new_lead.id} for {new_lead.name}")
    return new_lead


@router.get("", response_model=List[LeadOutSchema])
async def list_leads(
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db)
):
    """Lists recent leads with pagination and optional status filter."""
    stmt = select(Lead).order_by(desc(Lead.created_at)).limit(limit)
    if status_filter:
        stmt = stmt.where(Lead.status == status_filter)
    result = await db.execute(stmt)
    leads = result.scalars().all()
    return leads


@router.get("/{lead_id}", response_model=LeadOutSchema)
async def get_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    """Fetches details of a specific lead by ID."""
    stmt = select(Lead).where(Lead.id == lead_id)
    result = await db.execute(stmt)
    lead = result.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/update-plan", response_model=LeadOutSchema)
async def update_lead_plan(payload: LeadUpdatePlanSchema, db: AsyncSession = Depends(get_db)):
    """Updates the selected incorporation package and professional fee amount."""
    stmt = select(Lead).where(Lead.id == payload.lead_id)
    result = await db.execute(stmt)
    lead = result.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead.package = payload.package
    lead.amount = payload.amount
    lead.status = "PLAN_SELECTED"
    await db.commit()
    await db.refresh(lead)
    return lead
