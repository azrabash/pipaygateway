#D:\Workspaces\codin\app\routes\payment.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.payment import Payment
from app.models.user import User
from app.schemas import PaymentCreate, PaymentResponse
from app.utils.security import get_current_user
import logging

router = APIRouter()

@router.post("/payments", response_model=PaymentResponse)
async def create_payment(
    payment: PaymentCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    """✅ Endpoint untuk membuat permintaan pembayaran"""
    user_email = current_user["email"]

    # 🔍 Cari user berdasarkan email
    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # 🚀 Simpan pembayaran
    new_payment = Payment(
        user_id=user.id, 
        amount=payment.amount, 
        method=payment.method, 
        status="pending"
    )
    
    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)

    logging.info(f"💳 Payment request {payment.amount} PI via {payment.method} by {user.username}")

    return new_payment

@router.get("/payments", response_model=list[PaymentResponse])
async def get_payments(
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    """✅ Endpoint untuk melihat riwayat pembayaran"""
    user_email = current_user["email"]

    # 🔍 Cari user berdasarkan email
    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # 🚀 Ambil daftar pembayaran user ini
    result = await db.execute(select(Payment).where(Payment.user_id == user.id))
    payments = result.scalars().all()

    return payments

@router.put("/payments/{payment_id}", response_model=PaymentResponse)
async def update_payment_status(
    payment_id: int,
    status: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """✅ Endpoint untuk mengubah status pembayaran"""
    valid_statuses = ["pending", "completed", "failed"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()

    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    # 🔍 Perbaiki validasi user (gunakan `current_user["id"]`)
    if payment.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this payment")

    payment.status = status
    await db.commit()
    await db.refresh(payment)

    logging.info(f"💳 Payment {payment_id} updated to {status}")

    return payment

