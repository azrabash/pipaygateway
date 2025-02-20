#app/utils/security.py

import bcrypt
import jwt
from datetime import datetime, timedelta
from app.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.config import settings
from datetime import datetime, timezone

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # ✅ Remark: Setup token authentication
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


# def create_access_token(data: dict, expires_delta: timedelta | None = None):
    # to_encode = data.copy()
    # expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # to_encode.update({"exp": expire})
    # return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        user_id: int = payload.get("id")  # ✅ Ambil user_id dari token

        if email is None or user_id is None:
            raise credentials_exception

        return {"email": email, "id": user_id}  # ✅ Kembalikan juga "id"

    except JWTError:
        raise credentials_exception


# def get_current_user(token: str = Depends(oauth2_scheme)):
    # """✅ Middleware untuk validasi JWT Token"""
    # credentials_exception = HTTPException(
        # status_code=status.HTTP_401_UNAUTHORIZED,
        # detail="Invalid authentication credentials",
        # headers={"WWW-Authenticate": "Bearer"},
    # )

    # try:
        # payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        # email: str = payload.get("sub")

        # if email is None:
            # raise credentials_exception

        # exp = payload.get("exp")
        # if exp is None or datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            # raise HTTPException(status_code=401, detail="Token expired")

        # return {"email": email}  # ✅ Remark: User berhasil divalidasi

    # except JWTError:
        # raise credentials_exception
