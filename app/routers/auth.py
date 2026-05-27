from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
from jose import JWTError, jwt

from ..database import get_db
from ..models import User
from ..schemas import UserCreate
from ..config import settings
from ..security import get_password_hash, verify_password, create_access_token

router = APIRouter(tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    user_name: str


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise credentials_exception

    return user


@router.post("/register", status_code=status.HTTP_201_CREATED)
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_in: dict, db: Session = Depends(get_db)):
    print("===== RAW REGISTER DATA =====")
    print(user_in)
    print("=============================")

    email = str(user_in.get("email", "")).strip().lower()
    password = str(user_in.get("password", "")).strip()
    name = str(user_in.get("name", "")).strip()

    if not email or not password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    if not name:
        name = email.split("@")[0]

    # 檢查 Email 是否已存在
    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    try:
        new_user = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=get_password_hash(password),
            name=name,
            phone=user_in.get("phone"),
            birthday=user_in.get("birthday"),
            likes=user_in.get("likes")
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User created successfully",
            "user_id": new_user.id,
            "user_name": new_user.name
        }

    except Exception as e:
        db.rollback()

        print("===== REGISTER ERROR =====")
        print(str(e))
        print("==========================")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    email = login_data.email.strip().lower()

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token = create_access_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "user_name": user.name or user.email
    }


@router.get("/check_name/{name}")
def check_name_exists(name: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == name).first()
    return {"exists": user is not None}