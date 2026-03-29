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
    # 1. 先檢查有沒有重複的景點名稱
    existing_spot = db.query(models.Spot).filter(models.Spot.name == payload.name).first()
    if existing_spot:
        raise HTTPException(status_code=400, detail="這個景點已經存在囉！")
        
    # 2. 手動產生 UUID 與台灣時間
    new_id = str(uuid.uuid4())
    tw_now = (datetime.now(timezone.utc) + timedelta(hours=8)).replace(tzinfo=None)
    
    # 3. 抓取經緯度，並呼叫函式自動計算洲際
    # 使用 getattr 防呆，確保即使前端沒傳經緯度，程式也不會死當
    lat = getattr(payload, 'latitude', None)
    lon = getattr(payload, 'longitude', None)
    calculated_region = get_region_by_coordinates(lat, lon)

    # 4. 建立要存入資料庫的物件
    spot = models.Spot(
        id=new_id,
        name=payload.name,
        category=payload.category,
        features=payload.features,   
        location=payload.location,
        hours=payload.hours,
        activities=payload.activities, 
        latitude=lat,               # 緯度
        longitude=lon,              # 經度
        region=calculated_region,   # 存入自動算好的洲際
        created_at=tw_now
    )
    
    # 5. 安全寫入資料庫
    try:
        db.add(spot)
        db.commit()
        db.refresh(spot)
        return spot
        
    except Exception as e:
        db.rollback() # 發生錯誤要回滾，避免資料庫卡住
        print(f"❌ Database Error: {e}") 
        raise HTTPException(status_code=500, detail=f"新增景點失敗: {str(e)}")
    
def get_region_by_coordinates(lat: float, lon: float) -> str:
    """
    透過經緯度自動判斷所屬洲際
    lat: 緯度 (-90 ~ 90)
    lon: 經度 (-180 ~ 180)
    """
    if lat is None or lon is None:
        return "Asia" # 防呆預設值

    # 1. 美洲 (Americas): 經度大約在 -170 到 -30 之間
    if -170 <= lon <= -30:
        return "Americas"
        
    # 2. 歐洲與非洲 (Europe & Africa): 經度大約在 -20 到 60 之間
    elif -20 <= lon <= 60:
        # 以地中海附近 (緯度 35 度) 作為歐非粗略分界
        if lat > 35:
            return "Europe"
        else:
            return "Africa"
            
    # 3. 亞洲與大洋洲 (Asia & Oceania): 經度大約在 60 到 180 之間
    elif 60 < lon <= 180:
        # ✨ 特別拉出台灣的精準座標 (緯度 21.8~25.3, 經度 120~122)
        if 21.8 <= lat <= 25.3 and 120 <= lon <= 122:
            return "Taiwan"
            
        # 以赤道偏南 (緯度 -10 度，印尼下方) 作為亞洲與大洋洲分界
        if lat > -10:
            return "Asia"
        else:
            return "Oceania"

    return "Asia" # 找不到的防呆預設