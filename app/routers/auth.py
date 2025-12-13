from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid # 用來產生 UUID

# 引入您的資料庫與模型
from ..database import get_db
from ..models import User
from ..schemas import UserCreate
# 引入剛剛建立的 security 工具
from ..security import get_password_hash, verify_password, create_access_token

router = APIRouter(tags=["auth"])

# 定義登入請求的格式 (前端傳來的 JSON)
class LoginRequest(BaseModel):
    email: str
    password: str

# 定義 Token 回傳格式 (回傳給前端的 JSON)
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    user_name: str

# --- 1. 註冊 API (POST /register) ---
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # 檢查 Email 是否已存在
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 產生新的 UUID
    new_id = str(uuid.uuid4())

    # 建立使用者物件 (注意：密碼要加密！)
    new_user = User(
        id=new_id,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password), # 這裡呼叫加密函式
        name=user_in.name,
        phone=user_in.phone,
        birthday=user_in.birthday,
        likes=user_in.likes
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User created successfully", "user_id": new_id}
    except Exception as e:
        db.rollback()
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# --- 2. 登入 API (POST /login) ---
@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    # 找使用者
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        #為了安全，不告訴他是帳號錯還是密碼錯
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # 驗證密碼
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # 製作 Token
    access_token = create_access_token(data={"sub": user.id})

    # 回傳 Token 與基本資訊給前端
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "user_name": user.name or user.email
    }
    
# --- 3. 檢查名稱是否重複 API (GET /check_name/{name}) ---
@router.get("/check_name/{name}")
def check_name_exists(name: str, db: Session = Depends(get_db)):
    # 在資料庫找找看有沒有這個名字
    user = db.query(User).filter(User.name == name).first()
    
    # 如果 user 存在，回傳 exists=True
    if user:
        return {"exists": True}
    else:
        return {"exists": False}