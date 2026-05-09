from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
import uuid
from datetime import datetime, timezone, timedelta
from typing import List

# 建立專屬的 router，網址前綴設為 /api/expenses
router = APIRouter(tags=["expenses"])

@router.post("/", response_model=schemas.ExpenseOut, status_code=201)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    
    # 🛡️ 防呆機制：檢查「分帳總和」有沒有等於「花費總金額」
    total_split = sum(detail.amount for detail in expense.split_details)
    
    # 處理浮點數誤差 (例如 33.33 + 33.33 + 33.34 = 100)
    if abs(total_split - expense.amount) > 0.01:
        raise HTTPException(status_code=400, detail="錯誤：分帳的總金額與花費總金額不符！")

    # 手動產生 UUID 與台灣時間
    new_id = str(uuid.uuid4())
    tw_now = (datetime.now(timezone.utc) + timedelta(hours=8)).replace(tzinfo=None)

    # 準備存入資料庫的 JSON 格式
    # 將 Pydantic 的 SplitDetail 物件轉回普通的 dict
    split_details_json = [detail.model_dump() for detail in expense.split_details]

    # 建立資料庫模型
    db_expense = models.Expense(
        id=new_id,
        itinerary_id=expense.itinerary_id,
        payer_id=expense.payer_id,
        description=expense.description,
        amount=expense.amount,
        currency=expense.currency,
        split_details=split_details_json, # 存入 JSON
        created_at=tw_now
    )
    
    # 安全寫入資料庫
    try:
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        return db_expense
    except Exception as e:
        db.rollback()
        print(f"❌ Database Error: {e}") 
        raise HTTPException(status_code=500, detail=f"新增花費失敗: {str(e)}")
    
@router.get("/itinerary/{itinerary_id}", response_model=List[schemas.ExpenseOut])
def get_itinerary_expenses(itinerary_id: str, db: Session = Depends(get_db)):
    # 到資料庫找出所有符合行程 ID 的花費
    # 並依照時間排序 (最新的在前面)
    expenses = db.query(models.Expense).filter(
        models.Expense.itinerary_id == itinerary_id
    ).order_by(models.Expense.created_at.desc()).all()
    
    return expenses
