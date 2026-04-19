# routers/collab.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Itinerary, User
from pydantic import BaseModel

router = APIRouter(prefix="/api/collab", tags=["Collaboration"])

class JoinTripRequest(BaseModel):
    user_id: str

# 1. 透過邀請碼加入行程
@router.post("/join/{invite_code}")
async def join_itinerary(
    invite_code: str, 
    payload: JoinTripRequest,
    db: Session = Depends(get_db), 
):
    # 根據 user_id 找使用者
    current_user = db.query(User).filter(User.id == payload.user_id).first()
    # 根據 code 尋找行程
    itinerary = db.query(Itinerary).filter(Itinerary.code == invite_code).first()
    
    if not itinerary:
        raise HTTPException(status_code=404, detail="找不到此行程，請檢查邀請碼是否正確")

    # 檢查是否為房主 (房主不用加入)
    if current_user.id == itinerary.owner_user_id:
        return {"message": "你是這個行程的建立者，無需加入", "itinerary_id": itinerary.id}
    
    # 檢查是否已經在協作名單中
    if current_user in itinerary.collaborators:
        return {"message": "你已經在這個行程的成員名單中囉！", "itinerary_id": itinerary.id}

    # ✨ 將使用者加入協作名單
    itinerary.collaborators.append(current_user)
    db.commit()
    
    return {
        "message": f"成功加入行程：{itinerary.title}", 
        "itinerary_id": itinerary.id
    }

# 2. 查看某個行程的成員名單 (房主 + 協作者)
@router.get("/members/{itinerary_id}")
async def get_members(itinerary_id: str, db: Session = Depends(get_db)):
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
    if not itinerary:
        raise HTTPException(status_code=404, detail="行程不存在")
        
    return {
        "owner": itinerary.owner.name,
        "collaborators": [user.name for user in itinerary.collaborators]
    }