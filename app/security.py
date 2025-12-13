from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import jwt

# 設定密鑰 (真實上線時應該要放在環境變數)
SECRET_KEY = "your-secret-key-keep-it-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt