from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import jwt

from .config import settings



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 1. 驗證密碼 (比對輸入的密碼 vs 資料庫的雜湊碼)
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password[:72], hashed_password)

# 2. 產生密碼雜湊 (把明碼加密)
def get_password_hash(password):
    return pwd_context.hash(password[:72])

# 3. 產生 JWT Token (通行證)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt