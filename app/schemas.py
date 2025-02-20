#D:\Workspaces\codin\app\schemas.py

from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


# ✅ Remark: Menambahkan validasi dengan Pydantic
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    
    
class TransactionCreate(BaseModel):
    receiver_id: int
    amount: float

class TransactionResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    amount: float
    status: str

class PaymentCreate(BaseModel):
    amount: float
    method: str  # ✅ Remark: Contoh method: "bank transfer", "crypto"

class PaymentResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    method: str
    status: str
