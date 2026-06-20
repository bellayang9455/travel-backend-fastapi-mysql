from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas
import uuid
import json # 如果需要除錯 JSON 可以用
from datetime import datetime, timedelta,timezone
from sqlalchemy import or_
from sqlalchemy import func

from sqlalchemy import func, or_, outerjoin

router = APIRouter(tags=["spots"])

# 列出所有景點，支援關鍵字搜尋
@router.get("/", response_model=List[schemas.SpotOut])
def list_spots(q: str = Query(None), db: Session = Depends(get_db)):
    # 直接在查詢層面就算好 review_count 和 avg_rating
    query = db.query(
        models.Spot,
        func.count(models.Review.id).label('review_count'),
        func.avg(models.Review.stars).label('avg_rating')
    ).outerjoin(
        models.Review, models.Spot.id == models.Review.spot_id
    ).group_by(
        models.Spot.id
    )
    
    # ✨ 新增：同時搜尋「名稱」與「地點」的模糊比對
    if q:
        search_keyword = f"%{q}%"
        query = query.filter(
            or_(
                models.Spot.name.like(search_keyword),
                models.Spot.location.like(search_keyword)
            )
        )
        
    # 執行查詢，這會回傳一組一組的 tuple: (Spot物件, 評論數, 平均星等)
    results = query.order_by(models.Spot.created_at.desc()).all()

    # 把算好的數據塞回 Spot 物件裡，讓 Pydantic (schemas.SpotOut) 可以順利解析
    spots = []
    for spot, count, avg in results:
        spot.review_count = count
        spot.avg_rating = round(avg, 1) if avg else 0.0
        spots.append(spot)
        
    return spots

# 檢查景點名稱是否存在
@router.get("/check_name")
def check_name_exists(name: str, db: Session = Depends(get_db)):
    if not name or len(name.strip()) < 1:
        return {"exists": False, "similar_names": []}

    # 用 like 支援中文的模糊搜尋
    similar_spots = db.query(models.Spot)\
        .filter(models.Spot.name.like(f"%{name}%"))\
        .limit(5)\
        .all()
    
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

#更新資料用
@router.get("/fix_regions")
def fix_old_spots_regions(db: Session = Depends(get_db)):
    """
    這是一支一次性的工具 API，用來把資料庫裡舊的景點，
    全部用經緯度重新計算一次 region 並存檔。
    """
    # 1. 抓出資料庫裡「所有的景點」
    all_spots = db.query(models.Spot).all()
    updated_count = 0
    
    # 2. 跑迴圈，一個一個幫它們算洲際
    for spot in all_spots:
        # 呼叫我們剛剛寫的魔法函式
        calculated_region = get_region_by_coordinates(spot.latitude, spot.longitude)
        
        # 覆寫原本的 region (可能原本是 NULL 或預設的 Asia)
        spot.region = calculated_region
        updated_count += 1
        
    # 3. 一次把所有變更存進資料庫
    try:
        db.commit()
        return {"message": f"🎉 太神啦！成功更新了 {updated_count} 筆舊景點的洲際分類！"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    
@router.put("/{spot_id}",response_model=schemas.SpotOut)
async def update_spot(spot_id: str, spot_data: schemas.SpotCreate, db: Session = Depends(get_db)):
    spot = db.query(models.Spot).filter(models.Spot.id == spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="找不到該景點")
    
    # 2. (選用) 檢查改名後是否跟別人重複 (排除自己目前的 id)
    existing_spot = db.query(models.Spot).filter(models.Spot.name == spot_data.name, models.Spot.id != spot_id).first()
    if existing_spot:
        raise HTTPException(status_code=400, detail="這個景點名稱已經存在囉！")

    # 3. 覆寫欄位資料
    spot.name = spot_data.name
    spot.category = spot_data.category
    spot.location = spot_data.location
    spot.hours = spot_data.hours
    spot.features = spot_data.features
    spot.activities = spot_data.activities
    
    # 將前端傳來的洲際也更新進去 (使用 getattr 防止前端沒傳時出錯)
    spot.region = getattr(spot_data, 'region', spot.region)
    
    # 4. 存檔並回傳
    try:
        db.commit()
        db.refresh(spot)
        return spot # 回傳更新後的景點資料
    except Exception as e:
        db.rollback()
        print(f"❌ Database Error: {e}") 
        raise HTTPException(status_code=500, detail=f"更新景點失敗: {str(e)}")