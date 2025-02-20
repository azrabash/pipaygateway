#  D:\Workspaces\codin\app\routes\auth.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, TokenResponse
from passlib.context import CryptContext
from app.utils.security import verify_password, create_access_token
from datetime import timedelta
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    logging.info(f"🔍 Checking user login: {user.email}")

    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar()

    if not existing_user:
        logging.warning("⚠️ User not found!")
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user.password, existing_user.password):
        logging.warning("❌ Invalid password!")
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # access_token = create_access_token(data={"sub": existing_user.email}, expires_delta=timedelta(minutes=30))
    access_token = create_access_token(
        data={"sub": existing_user.email, "id": existing_user.id},  # ✅ Pastikan "id" ada di dalam token
        expires_delta=timedelta(minutes=30)
    )


    logging.info(f"✅ Login successful for {user.email}")

    return {"access_token": access_token, "token_type": "bearer"}
    

@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    logging.info(f"📌 Checking if email exists: {user.email}")

    try:
        # ✅ Remark: Normalisasi email ke huruf kecil
        user.email = user.email.lower()

        # ✅ Remark: Cek apakah email atau username sudah ada
        result = await db.execute(select(User).where((User.email == user.email) | (User.username == user.username)))
        existing_user = result.scalar()

        if existing_user:
            if existing_user.email == user.email:
                logging.warning(f"⚠️ Email {user.email} already registered!")
                raise HTTPException(status_code=400, detail="Email already registered")
            if existing_user.username == user.username:
                logging.warning(f"⚠️ Username {user.username} already taken!")
                raise HTTPException(status_code=400, detail="Username already taken")

        logging.info("✅ Email & Username available. Proceeding with registration.")

        # ✅ Remark: Hash password sebelum menyimpan
        logging.info("🔒 Hashing password...")
        hashed_password = pwd_context.hash(user.password)

        new_user = User(username=user.username, email=user.email, password=hashed_password)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        logging.info(f"🎉 User {user.email} registered successfully!")

        return {"message": "User registered successfully", "user": new_user.email}
    
    except SQLAlchemyError as e:
        logging.error(f"❌ Database error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error")
