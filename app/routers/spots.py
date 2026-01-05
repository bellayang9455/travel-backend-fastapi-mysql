from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas
import uuid
import json # 如果需要除錯 JSON 可以用
from datetime import datetime, timedelta,timezone
from sqlalchemy import or_

router = APIRouter(tags=["spots"])

# 列出所有景點，支援關鍵字搜尋
@router.get("/", response_model=List[schemas.SpotOut])
def list_spots(q: str = Query(None, description="關鍵字"), db: Session = Depends(get_db)):
    query = db.query(models.Spot)
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                models.Spot.name.ilike(search_term),
                models.Spot.location.ilike(search_term),
                models.Spot.category.ilike(search_term),
                models.Spot.features.ilike(search_term) # 連特色標籤也一起搜
            )
        )
    spots = query.order_by(models.Spot.created_at.desc()).all()
    return spots

# 檢查景點名稱是否存在
@router.get("/check_name")
def check_name_exists(name: str, db: Session = Depends(get_db)):
    if not name or len(name.strip()) < 1:
        return {"exists": False, "similar_names": []}

    # 用 ilike (Case-insensitive LIKE) 做模糊搜尋
    # 限制只回傳前 5 筆，避免因為輸入 "台" 就回傳幾百筆
    similar_spots = db.query(models.Spot)\
        .filter(models.Spot.name.ilike(f"%{name}%"))\
        .limit(5)\
        .all()
    
    # 回傳找到的名稱列表，讓前端顯示給使用者看
    return {
        "exists": len(similar_spots) > 0,
        "similar_names": [s.name for s in similar_spots]
    }

@router.post("/", response_model=schemas.SpotOut, status_code=201)
def create_spot(payload: schemas.SpotCreate, db: Session = Depends(get_db)):
    # 先檢查有沒有重複的景點名稱
    existing_spot = db.query(models.Spot).filter(models.Spot.name == payload.name).first()
    if existing_spot:
        raise HTTPException(status_code=400, detail="這個景點已經存在囉！")
    # 手動產生 UUID
    new_id = str(uuid.uuid4())
    
    tw_now = (datetime.now(timezone.utc) + timedelta(hours=8)).replace(tzinfo=None)
    spot = models.Spot(
        id=new_id,
        name=payload.name,
        category=payload.category,
        features=payload.features,   # 這裡會接收前端傳來的 JSON/Array
        location=payload.location,
        hours=payload.hours,
        activities=payload.activities, # 這裡會接收前端傳來的 JSON/Array
        created_at=tw_now
    )
    
    try:
        db.add(spot)
        db.commit()
        db.refresh(spot)
        return spot
        
    except Exception as e:
        db.rollback() # 發生錯誤要回滾，避免資料庫卡住
        print(f"❌ Database Error: {e}") # 會印在終端機，方便你看錯誤原因
        # 回傳 500 但帶有詳細訊息
        raise HTTPException(status_code=500, detail=f"新增景點失敗: {str(e)}")