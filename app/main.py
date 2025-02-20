#D:\Workspaces\codin\app\main.py
import logging
from fastapi import FastAPI
from app.routes.auth import router as auth_router
from app.routes.user import router as user_router  # ✅ Tambahkan ini
from app.routes.transaction import router as transaction_router  # ✅ Tambahkan ini
from app.routes.payment import router as payment_router  # ✅ Tambahkan ini
from app.routes.pi_integration import router as pi_router
from app.config import settings
print(settings.PI_API_KEY)  # Tambahkan sementara di `main.py`

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

app.include_router(pi_router, prefix="/pi", tags=["Pi Network"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(user_router, prefix="", tags=["Users"])
app.include_router(transaction_router, prefix="", tags=["Transactions"])  # ✅ Pastikan ini ada
app.include_router(payment_router, prefix="", tags=["Payments"])  # ✅ Pastikan ini ada

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(user_router, prefix="", tags=["Users"])  # ✅ Pastikan ini ada

@app.get("/")
def root():
    logging.info("📌 Root endpoint accessed")
    return {"message": "Hello, PI Wallet!"}

