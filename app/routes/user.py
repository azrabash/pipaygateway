#  D:\Workspaces\codin\app\routes\user.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select  # ✅ Remark: Gunakan select() untuk query async
from app.database import get_db
from app.models.user import User
from app.utils.security import get_current_user  # ✅ Remark: Tambahkan JWT authentication
import logging

router = APIRouter()

@router.get("/users")
async def get_users(
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(get_current_user)  # ✅ Remark: Proteksi endpoint dengan JWT
):
    """✅ Endpoint ini hanya bisa diakses jika user memiliki JWT Token yang valid"""
    logging.info(f"🔍 User {current_user['email']} mengakses /users")

    result = await db.execute(select(User))  # ✅ Remark: Gunakan ORM SQLAlchemy, bukan query langsung
    users = result.scalars().all()

    return {"users": [{"id": user.id, "username": user.username, "email": user.email} for user in users]}
