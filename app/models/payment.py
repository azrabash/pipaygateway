#D:\Workspaces\codin\app\models\payment.py

from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(String, nullable=False)  # ✅ Remark: Metode pembayaran (misalnya: "bank transfer", "crypto")
    status = Column(String, default="pending")  # ✅ Remark: Status pembayaran ("pending", "completed", "failed")

    user = relationship("User", foreign_keys=[user_id])
