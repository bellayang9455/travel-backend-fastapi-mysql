from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from pydantic import BaseModel
import uuid

from ..database import get_db
from .. import models, schemas
from ..utils import gen_uuid

router = APIRouter(prefix="/itineraries", tags=["itineraries"])

# --- 1. 定義本地需要的 Schema (為了支援編輯模式) ---
# 這是為了讓前端 User.vue 能夠拿到 "流水號 ID"，才能做拖曳和刪除
# 原本的 schemas.SpotOut 只有景點資料，沒有關聯表的 ID

class ItineraryItemOut(BaseModel):
    id: int               # 這就是 itinerary_spots 的流水號 ID
    day_order: int        # 排序順序
    spot: schemas.SpotOut # 包含原本的景點詳細資料

    class Config:
        from_attributes = True

class ItineraryEditorOut(BaseModel):
    id: str
    title: str
    spots: List[ItineraryItemOut] # 這裡回傳的是包了一層的結構

    class Config:
        from_attributes = True

# 新增景點用的輸入模型
class ItemAdd(BaseModel):
    spot_id: str

# 排序用的輸入模型
class ReorderItem(BaseModel):
    item_id: int 
    new_order: int

# --- API 實作 ---

# 1. [搜尋/列表] 這是給「首頁」看的，保持您原本的邏輯
@router.get("/", response_model=List[schemas.ItineraryOut])
def list_itineraries(
    q: str = Query("", description="關鍵字"),
    budget_lte: int | None = Query(None, description="最大預算"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Itinerary).options(
        joinedload(models.Itinerary.spots).joinedload(models.ItinerarySpot.spot)
    )
    if q:
        like = f"%{q}%"
        query = query.filter(
            (models.Itinerary.title.like(like)) |
            (models.Itinerary.transport.like(like))
        )
    if budget_lte is not None:
        query = query.filter(models.Itinerary.budget <= budget_lte)

    items = query.order_by(models.Itinerary.created_at.desc()).all()
    
    # 轉換成原本 schema 需要的格式 (扁平化景點)
    result = []
    for it in items:
        # 這裡只取 spot 資料，符合首頁顯示需求
        spots_data = [schemas.SpotOut.model_validate(is_rel.spot) for is_rel in it.spots]
        result.append(
            schemas.ItineraryOut(
                id=it.id,
                code=it.code,
                title=it.title,
                budget=it.budget,
                travel_time=it.travel_time,
                lodging=it.lodging,
                transport=it.transport,
                owner_user_id=it.owner_user_id,
                created_at=it.created_at,
                spots=spots_data,
            )
        )
    return result

# 2. [使用者專用] 取得某人的行程 (給 User.vue 用的，包含流水號 ID)
@router.get("/user/{user_id}", response_model=List[ItineraryEditorOut])
def get_user_itineraries(user_id: str, db: Session = Depends(get_db)):
    itineraries = db.query(models.Itinerary).filter(models.Itinerary.owner_user_id == user_id).all()
    
    # 手動排序裡面的 spots
    for itin in itineraries:
        # 依照 day_order 排序，如果沒有就排最後
        itin.spots.sort(key=lambda x: x.day_order if x.day_order is not None else 999)
        
    return itineraries

# 3. [取得單一] 詳細資料
@router.get("/{itinerary_id}", response_model=schemas.ItineraryOut)
def get_itinerary(itinerary_id: str, db: Session = Depends(get_db)):
    it = db.query(models.Itinerary).options(
        joinedload(models.Itinerary.spots).joinedload(models.ItinerarySpot.spot)
    ).filter(models.Itinerary.id == itinerary_id).first()
    if not it:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    spots_data = [schemas.SpotOut.model_validate(is_rel.spot) for is_rel in it.spots]
    
    # 這裡必須手動建構 ItineraryOut，因為 spots 格式不同
    return schemas.ItineraryOut(
        id=it.id,
        code=it.code,
        title=it.title,
        budget=it.budget,
        travel_time=it.travel_time,
        lodging=it.lodging,
        transport=it.transport,
        owner_user_id=it.owner_user_id,
        created_at=it.created_at,
        spots=spots_data, 
    )

# 4. [建立] 新增行程表
@router.post("/", response_model=schemas.ItineraryOut, status_code=201)
def create_itinerary(payload: schemas.ItineraryCreate, db: Session = Depends(get_db)):
    owner = db.query(models.User).filter_by(id=payload.owner_user_id).first()
    if not owner:
        raise HTTPException(status_code=400, detail="Owner user not found")

    # 使用您原本的 gen_uuid 或是 Python 內建 uuid
    itinerary_id = gen_uuid() 
    code = f"TRIP-{itinerary_id[:8].upper()}"
    
    it = models.Itinerary(
        id=itinerary_id,
        code=code,
        title=payload.title,
        budget=payload.budget,
        travel_time=payload.travel_time,
        lodging=payload.lodging,
        transport=payload.transport,
        owner_user_id=payload.owner_user_id,
    )
    db.add(it)
    db.flush()

    # 如果建立時有帶入 spot_ids，依序加入
    current_order = 0
    for sid in payload.spot_ids:
        db.add(models.ItinerarySpot(
            itinerary_id=it.id, 
            spot_id=sid,
            day_order=current_order # 設定順序
        ))
        current_order += 1

    db.commit()
    db.refresh(it)

    # 重新讀取以取得關聯
    it = db.query(models.Itinerary).options(
        joinedload(models.Itinerary.spots).joinedload(models.ItinerarySpot.spot)
    ).get(it.id)
    
    spots_data = [schemas.SpotOut.model_validate(is_rel.spot) for is_rel in it.spots]
    
    return schemas.ItineraryOut(
        id=it.id,
        code=it.code,
        title=it.title,
        budget=it.budget,
        travel_time=it.travel_time,
        lodging=it.lodging,
        transport=it.transport,
        owner_user_id=it.owner_user_id,
        created_at=it.created_at,
        spots=spots_data,
    )

# --- 以下是新增的功能 ---

# 5. [加入景點] 支援重複加入，自動計算順序
@router.post("/{itinerary_id}/add_spot")
def add_spot_to_itinerary(itinerary_id: str, data: ItemAdd, db: Session = Depends(get_db)):
    # 找目前最後一個順序
    last_item = db.query(models.ItinerarySpot).filter(models.ItinerarySpot.itinerary_id == itinerary_id)\
                  .order_by(models.ItinerarySpot.day_order.desc()).first()
    new_order = (last_item.day_order + 1) if last_item and last_item.day_order is not None else 0

    new_item = models.ItinerarySpot(
        itinerary_id=itinerary_id,
        spot_id=data.spot_id,
        day_order=new_order,
        note=""
    )
    db.add(new_item)
    db.commit()
    return {"message": "Success"}

# 6. [更新排序] 前端拖曳完後呼叫
@router.post("/{itinerary_id}/reorder")
def reorder_itinerary(itinerary_id: str, items: List[ReorderItem], db: Session = Depends(get_db)):
    for item in items:
        # 用唯一的 id (流水號) 找，精準定位是哪一次的景點要移動
        db_item = db.query(models.ItinerarySpot).filter(models.ItinerarySpot.id == item.item_id).first()
        
        if db_item and db_item.itinerary_id == itinerary_id:
            db_item.day_order = item.new_order
    db.commit()
    return {"message": "Order updated"}

# 7. [刪除項目] 刪除行程中的某個景點 (用流水號刪除)
@router.delete("/item/{item_id}")
def delete_itinerary_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.ItinerarySpot).filter(models.ItinerarySpot.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
    return {"message": "Deleted"}

# 8. [刪除行程] 刪除整本行程 (包含裡面的所有景點紀錄)
@router.delete("/{itinerary_id}")
def delete_itinerary(itinerary_id: str, db: Session = Depends(get_db)):
    # 1. 找到行程
    itinerary = db.query(models.Itinerary).filter(models.Itinerary.id == itinerary_id).first()
    
    if not itinerary:
        raise HTTPException(status_code=404, detail="行程不存在")
    
    # 2. 刪除
    # 由於 models.py 裡設定了 cascade="all, delete-orphan"
    # SQLAlchemy 會自動幫您把關聯的 itinerary_spots 也刪掉，不用手動刪
    db.delete(itinerary)
    db.commit()
    
    return {"message": "行程已完整刪除"}