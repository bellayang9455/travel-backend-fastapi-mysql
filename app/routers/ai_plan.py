# routers/ai_plan.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import google.generativeai as genai
from sqlalchemy.orm import Session
import json
import uuid

# 引入你的 models 和 database
from ..models import Spot
from ..database import get_db
from ..config import settings

router = APIRouter(prefix="/api", tags=["AI Planner"])

# 👇 你的 API KEY
GENAI_API_KEY = settings.gemini_api_key
genai.configure(api_key=GENAI_API_KEY)

class TripRequest(BaseModel):
    destination: str
    days: int
    style: str

@router.post("/generate_itinerary")
async def generate_itinerary(request: TripRequest, db: Session = Depends(get_db)):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        你是一個旅遊資料庫助手。請幫我規劃「{request.destination}」的「{request.days}天」行程，風格為「{request.style}」。
        
        請務必考量景點之間的距離與順路程度。
        請不要回傳任何聊天文字，**只回傳一個純 JSON 陣列 (Array)**。
        陣列中的每個物件代表一個景點，格式如下：
        [
            {{
                "name": "景點名稱",
                "description": "50字以內的簡介",
                "category": "請從[自然生態, 歷史人文, 在地美食, 休閒娛樂, 購物商圈]選一個最接近的",
                "location": "所在的行政區",
                "address": "完整地址",
                "latitude": 緯度(數字, 請精準),
                "longitude": 經度(數字, 請精準),
                "day": 第幾天(數字),
                "time_of_day": "上午/下午/晚上",
                "transportation": "從上個景點過來的交通建議 (例如：步行 5 分鐘 / 搭捷運紅線 10 分鐘)。如果是當天第一個景點，請寫 '自行前往'。"
            }}
        ]
        """

        response = model.generate_content(prompt)
        
        # 處理回傳
        if not response.text:
            raise ValueError("AI 沒有回傳內容")

        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        itinerary_data = json.loads(cleaned_text)

        # 寫入資料庫 (這裡維持原本邏輯)
        for spot_data in itinerary_data:
            existing_spot = db.query(Spot).filter(Spot.name == spot_data['name']).first()
            if not existing_spot:
                new_spot = Spot(
                    id=str(uuid.uuid4()),
                    name=spot_data['name'],
                    category=spot_data.get('category'),
                    location=spot_data.get('location'),
                    hours="09:00-18:00",
                    latitude=spot_data.get('latitude'),
                    longitude=spot_data.get('longitude')
                )
                db.add(new_spot)
                try:
                    db.commit()
                except:
                    db.rollback()
        
        return {"result": itinerary_data}

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")