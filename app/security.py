from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def safe_password(password: str) -> str:
    # bcrypt 最大 72 bytes
    return password.encode("utf-8")[:72].decode("utf-8", errors="ignore")


def get_password_hash(password: str):
    password = safe_password(password)
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    plain_password = safe_password(plain_password)
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt