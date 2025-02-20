#D:\Workspaces\codin\app\routes\pi_integration.py

import requests
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel  # Pindahkan import ke atas
from app.config import settings
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import logging

router = APIRouter()

# Konfigurasi API Pi Network
PI_API_URL = "https://api.minepi.com/v2"
PI_API_KEY = settings.PI_API_KEY

# Model untuk pembayaran
class PaymentRequest(BaseModel):
    amount: float
    uid: str  # Mengubah user_id dari int ke uid sebagai string


@router.get("/auth/pi-login")
def pi_login():
    """Menghasilkan URL login Pi Network"""
    return {"pi_auth_url": f"pi://auth?client_id={settings.PI_APP_ID}&response_type=code"}

@router.post("/auth/pi-callback")
def pi_callback(auth_code: str):
    """Menangani callback autentikasi dari Pi Network"""
    response = requests.post(
        f"{PI_API_URL}/me",
        headers={"Authorization": f"Bearer {auth_code}"},
    )
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Gagal autentikasi dengan Pi")
    return response.json()

@router.post("/payments/create")
async def create_payment(payment: PaymentRequest, db: AsyncSession = Depends(get_db)):
    """Membuat pembayaran melalui Pi Network"""
    
    # 🔹 Validasi bahwa UID tidak boleh kosong
    if not payment.uid or payment.uid.strip() == "":
        raise HTTPException(status_code=400, detail="UID tidak boleh kosong atau null")

    payload = {
        "amount": payment.amount,
        "memo": "Pembayaran melalui Pi Network",
        "metadata": {"uid": payment.uid},
        "uid": payment.uid,  # Pastikan UID berupa string
    }

    response = requests.post(
        f"{PI_API_URL}/payments",
        json=payload,
        headers={"Authorization": f"Key {settings.PI_API_KEY}"},
    )

    logging.warning(f"Pi API Response: {response.status_code} - {response.text}")

    if response.status_code != 201:
        raise HTTPException(status_code=400, detail=f"Gagal membuat pembayaran: {response.text}")

    return response.json()



@router.post("/auth/pi-callback")
def pi_callback(auth_code: str):
    """Menangani callback autentikasi dari Pi Network"""
    response = requests.post(
        f"{PI_API_URL}/me",
        headers={"Authorization": f"Bearer {auth_code}"},
    )
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Gagal autentikasi dengan Pi")

    user_data = response.json()
    pi_uid = user_data.get("uid")  # Simpan UID dari Pi

    # ✅ Simpan `pi_uid` ke database sebagai identitas user di Pi
    return {"pi_uid": pi_uid}



@router.post("/payments/complete")
def complete_payment(payment_id: str):
    """Menyelesaikan pembayaran setelah Pi mengonfirmasi"""
    response = requests.post(
        f"{PI_API_URL}/payments/{payment_id}/complete",
        headers={"Authorization": f"Key {PI_API_KEY}"},
    )
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Gagal menyelesaikan pembayaran")
    return response.json()

@router.post("/payments/cancel")
def cancel_payment(payment_id: str):
    """Membatalkan pembayaran jika terjadi kesalahan"""
    response = requests.post(
        f"{PI_API_URL}/payments/{payment_id}/cancel",
        headers={"Authorization": f"Key {PI_API_KEY}"},
    )
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Gagal membatalkan pembayaran")
    return response.json()
