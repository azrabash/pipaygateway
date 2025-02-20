#D:\Workspaces\codin\app\routes\transaction.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.database import get_db
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas import TransactionCreate, TransactionResponse
from app.utils.security import get_current_user
from app.utils.pi_network import get_transaction

import logging

router = APIRouter()

@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction_status(
    transaction_id: int,
    status: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """✅ Endpoint untuk mengubah status transaksi"""
    valid_statuses = ["pending", "completed", "failed"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    result = await db.execute(
        select(Transaction).where(Transaction.id == transaction_id).options(joinedload(Transaction.sender))
    )
    transaction = result.scalar_one_or_none()

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.sender.email != current_user["email"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this transaction")

    transaction.status = status
    await db.commit()
    await db.refresh(transaction)

    logging.info(f"🔄 Transaction {transaction_id} updated to {status}")

    return transaction


@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    """✅ Endpoint untuk mengirim PI Coin ke user lain"""
    sender_email = current_user["email"]

    # 🔍 Cari sender berdasarkan email
    result = await db.execute(select(User).where(User.email == sender_email))
    sender = result.scalar_one_or_none()

    if sender is None:
        raise HTTPException(status_code=404, detail="Sender not found")

    # 🔍 Cek apakah receiver ada di database
    result = await db.execute(select(User).where(User.id == transaction.receiver_id))
    receiver = result.scalar_one_or_none()

    if receiver is None:
        raise HTTPException(status_code=404, detail="Receiver not found")

    if sender.id == receiver.id:
        raise HTTPException(status_code=400, detail="Cannot send to yourself")

    # 🚀 Buat transaksi
    new_transaction = Transaction(
        sender_id=sender.id, 
        receiver_id=receiver.id, 
        amount=transaction.amount,
        status="pending"
    )
    
    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction)

    logging.info(f"💰 {sender.username} sent {transaction.amount} PI to {receiver.username}")

    return new_transaction

@router.get("/transactions", response_model=list[TransactionResponse])
async def get_transactions(
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    """✅ Endpoint untuk melihat riwayat transaksi"""
    sender_email = current_user["email"]

    # 🔍 Cari user berdasarkan email
    result = await db.execute(select(User).where(User.email == sender_email))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # 🚀 Ambil transaksi yang terkait dengan user ini
    result = await db.execute(
        select(Transaction).where((Transaction.sender_id == user.id) | (Transaction.receiver_id == user.id))
    )
    transactions = result.scalars().all()

    return transactions


@router.put("/transactions/{transaction_id}/validate", response_model=TransactionResponse)
async def validate_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """✅ Validasi transaksi dengan PI Network"""
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id))
    transaction = result.scalar_one_or_none()

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # 🔍 Cek transaksi di PI Blockchain
    pi_transaction = await get_transaction(str(transaction_id))
    if not pi_transaction or pi_transaction.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Transaction is not completed on PI Network")

    # 🚀 Update status transaksi jika sudah tervalidasi
    transaction.status = "completed"
    await db.commit()
    await db.refresh(transaction)

    logging.info(f"✅ Transaction {transaction_id} validated with PI Network")

    return transaction
