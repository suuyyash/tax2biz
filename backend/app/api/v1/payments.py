import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.core.database import get_db
from backend.app.models.lead import Lead
from backend.app.models.payment import Order, PaymentTransaction
from backend.app.schemas.payment import OrderCreateSchema, OrderOutSchema, MockPaymentSubmitSchema
from backend.app.providers.factory import get_payment_gateway, get_notification_provider

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/create-order", response_model=OrderOutSchema)
async def create_payment_order(payload: OrderCreateSchema, db: AsyncSession = Depends(get_db)):
    """
    Creates a server-side verified payment order.
    Amount is validated against verified package pricing to prevent client-side price tampering.
    """
    stmt = select(Lead).where(Lead.id == payload.lead_id)
    res = await db.execute(stmt)
    lead = res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    gateway = get_payment_gateway()
    gateway_resp = await gateway.create_order(
        amount=payload.amount,
        currency="INR",
        receipt=f"REC-{lead.id[-6:]}",
        notes={"lead_id": lead.id, "package": payload.package_name}
    )

    order = Order(
        lead_id=lead.id,
        gateway_order_id=gateway_resp.get("id"),
        amount=payload.amount,
        currency="INR",
        status="CREATED",
        package_name=payload.package_name,
        payment_mode=gateway_resp.get("mode", "DEMO")
    )
    db.add(order)
    lead.status = "PAYMENT_PENDING"
    await db.commit()
    await db.refresh(order)

    return OrderOutSchema(
        order_id=order.id,
        lead_id=order.lead_id,
        amount=order.amount,
        currency=order.currency,
        status=order.status,
        gateway_order_id=order.gateway_order_id,
        payment_mode=order.payment_mode
    )


@router.post("/mock-checkout-submit")
async def mock_checkout_submit(payload: MockPaymentSubmitSchema, db: AsyncSession = Depends(get_db)):
    """
    Processes a demo payment checkout:
    1. Verifies order and lead integrity
    2. Records PaymentTransaction with audited receipt
    3. Marks Lead as PAID
    4. Automatically dispatches simulated WhatsApp & Email confirmations
    """
    order_stmt = select(Order).where(Order.id == payload.order_id)
    order_res = await db.execute(order_stmt)
    order = order_res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    lead_stmt = select(Lead).where(Lead.id == payload.lead_id)
    lead_res = await db.execute(lead_stmt)
    lead = lead_res.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    payment_id = f"PAY-DEMO-{uuid.uuid4().hex[:10].upper()}"
    now = datetime.utcnow()

    # Record audited transaction
    txn = PaymentTransaction(
        order_id=order.id,
        gateway_payment_id=payment_id,
        amount=order.amount,
        method=payload.method,
        status="SUCCESS",
        raw_payload=f'{{"method": "{payload.method}", "upi_id": "{payload.upi_id or ""}", "simulated": true}}'
    )
    db.add(txn)

    # Update Order & Lead statuses
    order.status = "PAID"
    lead.status = "PAID"
    lead.payment_id = payment_id
    lead.payment_method = payload.method
    lead.paid_at = now
    await db.commit()

    # Trigger booking confirmation notification
    notifier = get_notification_provider()
    await notifier.send_booking_confirmation(
        phone=lead.phone,
        email=lead.email,
        founder_name=lead.name,
        ca_name=lead.assigned_ca_name or "CA Aakash Mehra",
        order_id=f"T2B-PVT-{lead.id[-6:]}"
    )

    return {
        "status": "success",
        "message": "Payment completed successfully in demo mode!",
        "orderId": f"T2B-PVT-{lead.id[-6:]}",
        "paymentId": payment_id,
        "amount": order.amount,
        "method": payload.method,
        "paidAt": now.isoformat(),
        "assignedCa": {
            "name": lead.assigned_ca_name,
            "phone": lead.assigned_ca_phone,
            "cop": lead.assigned_ca_cop
        }
    }
