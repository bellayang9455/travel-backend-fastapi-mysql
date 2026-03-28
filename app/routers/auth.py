from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer # ✨ 新增這個
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
from jose import JWTError, jwt # ✨ 新增這個 (用來解碼 Token)

# 引入您的資料庫與模型
from ..database import get_db
from ..models import User
from ..schemas import UserCreate
# 引入 config 設定 (為了拿 SECRET_KEY)
from ..config import settings 
from ..security import get_password_hash, verify_password, create_access_token

router = APIRouter(tags=["auth"])

# ✨ 定義 Token 來源：告訴 FastAPI Token 會放在 Header 的 Authorization 欄位
# tokenUrl="auth/login" 是為了讓 Swagger UI 的 "Authorize" 按鈕知道去哪裡登入
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    user_name: str

#  取得當前登入使用者 (驗證 Token) 
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1. 解碼 Token
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub") # 從 Token 拿出 user_id
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 2. 去資料庫找這個人
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    # 3. 回傳使用者物件 (這樣 collab.py 就能拿到 current_user 了！)
    return user


#  1. 註冊 API (維持不變) 
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_id = str(uuid.uuid4())

    new_user = User(
        id=new_id,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
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

#  2. 登入 API (維持不變) 
@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
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
    
#  3. 檢查名稱是否重複 API (維持不變) 
@router.get("/check_name/{name}")
def check_name_exists(name: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == name).first()
    if user:
        return {"exists": True}
    else:
        return {"exists": False}