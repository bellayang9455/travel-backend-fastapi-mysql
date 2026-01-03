from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from pydantic import BaseModel
import uuid

from ..database import get_db
from .. import models, schemas
from ..utils import gen_uuid
from ..routers.auth import get_current_user

router = APIRouter(tags=["itineraries"])

# ==========================================
# 👇 補上缺失的 Schema 定義 (放在這裡)
# ==========================================

# 1. 給編輯器用的
class ItineraryItemOut(BaseModel):
    id: int               # itinerary_spots 的流水號 ID
    day_order: int        # 排序順序
    spot: schemas.SpotOut # 包含原本的景點詳細資料

    class Config:
        from_attributes = True

class ItineraryEditorOut(BaseModel):
    id: str
    title: str
    spots: List[ItineraryItemOut] 

    class Config:
        from_attributes = True

# 2. 給 AI 儲存用的 (就是你原本缺少的這兩個！)
class SpotData(BaseModel):
    name: str
    day: int
    description: Optional[str] = None

class SaveAiTripRequest(BaseModel):
    title: str
    spots: List[SpotData]

# 3. 其他功能用的
class ItemAdd(BaseModel):
    spot_id: str

class ReorderItem(BaseModel):
    item_id: int 
    new_order: int

# ==========================================
# API 實作
# ==========================================

# 1. [搜尋/列表]
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
    
    result = []
    for it in items:
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

# 2. [使用者專用]
@router.get("/user/{user_id}", response_model=List[ItineraryEditorOut])
def get_user_itineraries(user_id: str, db: Session = Depends(get_db)):
    itineraries = db.query(models.Itinerary).filter(models.Itinerary.owner_user_id == user_id).all()
    
    for itin in itineraries:
        itin.spots.sort(key=lambda x: x.day_order if x.day_order is not None else 999)
        
    return itineraries

# 3. [取得單一]
@router.get("/{itinerary_id}", response_model=schemas.ItineraryOut)
def get_itinerary(itinerary_id: str, db: Session = Depends(get_db)):
    it = db.query(models.Itinerary).options(
        joinedload(models.Itinerary.spots).joinedload(models.ItinerarySpot.spot)
    ).filter(models.Itinerary.id == itinerary_id).first()
    if not it:
        raise HTTPException(status_code=404, detail="Itinerary not found")

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

# 4. [建立]
@router.post("/", response_model=schemas.ItineraryOut, status_code=201)
def create_itinerary(payload: schemas.ItineraryCreate, db: Session = Depends(get_db)):
    owner = db.query(models.User).filter_by(id=payload.owner_user_id).first()
    if not owner:
        raise HTTPException(status_code=400, detail="Owner user not found")

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

    current_order = 0
    for sid in payload.spot_ids:
        db.add(models.ItinerarySpot(
            itinerary_id=it.id, 
            spot_id=sid,
            day_order=current_order
        ))
        current_order += 1

    db.commit()
    db.refresh(it)

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

# 5. [加入景點]
@router.post("/{itinerary_id}/add_spot")
def add_spot_to_itinerary(itinerary_id: str, data: ItemAdd, db: Session = Depends(get_db)):
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

# 6. [更新排序]
@router.post("/{itinerary_id}/reorder")
def reorder_itinerary(itinerary_id: str, items: List[ReorderItem], db: Session = Depends(get_db)):
    for item in items:
        db_item = db.query(models.ItinerarySpot).filter(models.ItinerarySpot.id == item.item_id).first()
        
        if db_item and db_item.itinerary_id == itinerary_id:
            db_item.day_order = item.new_order
    db.commit()
    return {"message": "Order updated"}

# 7. [刪除項目]
@router.delete("/item/{item_id}")
def delete_itinerary_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.ItinerarySpot).filter(models.ItinerarySpot.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
    return {"message": "Deleted"}

# 8. [刪除行程]
@router.delete("/{itinerary_id}")
def delete_itinerary(itinerary_id: str, db: Session = Depends(get_db)):
    itinerary = db.query(models.Itinerary).filter(models.Itinerary.id == itinerary_id).first()
    
    if not itinerary:
        raise HTTPException(status_code=404, detail="行程不存在")
    
    db.delete(itinerary)
    db.commit()
    return {"message": "行程已完整刪除"}

# 9. [AI 轉存行程] 
@router.post("/from_ai") # 修正：這裡應該是 post，且路徑不要重複
async def create_itinerary_from_ai(
    request: SaveAiTripRequest, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    try:
        # 1. 建立一個新的行程表
        new_itinerary = models.Itinerary(  # 修正：加上 models.
            id=str(uuid.uuid4()),
            code=str(uuid.uuid4())[:8],
            title=request.title,
            owner_user_id=current_user.id
        )
        db.add(new_itinerary)
        db.flush()

        # 2. 把景點一個一個加進去
        for index, spot_data in enumerate(request.spots):
            # 修正：加上 models.Spot
            db_spot = db.query(models.Spot).filter(models.Spot.name == spot_data.name).first()
            
            if db_spot:
                # 修正：加上 models.ItinerarySpot
                new_link = models.ItinerarySpot(
                    itinerary_id=new_itinerary.id,
                    spot_id=db_spot.id,
                    day_order=spot_data.day,
                    note=spot_data.description
                )
                db.add(new_link)

        db.commit()
        return {"message": "成功加入我的行程！", "itinerary_id": new_itinerary.id}

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="儲存行程失敗")