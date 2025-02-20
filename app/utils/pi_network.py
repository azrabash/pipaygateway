#D:\Workspaces\codin\app\utils\pi_network.py

import httpx
import logging
from app.config import settings

BASE_URL = "https://blockexplorer.minepi.com/testnet"

async def get_transaction(tx_id: str):
    """✅ Mengambil detail transaksi dari PI Network"""
    headers = {"Authorization": f"Bearer {settings.PI_API_KEY}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/transactions/{tx_id}", headers=headers)

    logging.info(f"🔍 API Request: {BASE_URL}/transactions/{tx_id}")
    logging.info(f"🔍 API Response: {response.status_code} - {response.text}")

    return response.json() if response.status_code == 200 else None

async def get_payment(payment_id: str):
    """✅ Mengambil detail pembayaran dari PI Network"""
    headers = {"Authorization": f"Bearer {settings.PI_API_KEY}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/payments/{payment_id}", headers=headers)
        return response.json() if response.status_code == 200 else None
