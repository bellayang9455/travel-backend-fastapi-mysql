from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json
import os
import uuid
import random
import google.generativeai as genai

from ..database import get_db
from .. import models

# 設定 API KEY (隨便填也沒關係，因為我們會切換到 Mock)
os.environ["GOOGLE_API_KEY"] = "AIzaSyDgueDETXpRg-QMRLwTAFw8GZMar-id1tk"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

router = APIRouter(prefix="/ai", tags=["ai"])

class AIPlanRequest(BaseModel):
    destination: str
    days: int
    budget: int
    style: str
    owner_id: str

# --- 🛠️ 備用方案：聰明的 Mock 資料生成器 ---
def get_mock_itinerary(destination, days, style):
    print(f"⚠️ 啟用備用 Mock 模式生成: {destination}")
    
    mock_db = {
        "台北": [
            {"name": "台北101觀景台", "category": "網美打卡", "description": "俯瞰整個台北市景。"},
            {"name": "士林夜市", "category": "在地美食", "description": "觀光客必訪夜市。"},
            {"name": "故宮博物院", "category": "歷史人文", "description": "中華文化瑰寶。"},
            {"name": "象山步道", "category": "自然生態", "description": "拍攝101夜景最佳點。"},
            {"name": "西門町", "category": "購物商圈", "description": "年輕人流行聖地。"}
        ],
        "台南": [
            {"name": "安平古堡", "category": "歷史人文", "description": "台灣最古老城堡。"},
            {"name": "文章牛肉湯", "category": "在地美食", "description": "台南必吃早餐。"},
            {"name": "奇美博物館", "category": "網美打卡", "description": "彷彿置身歐洲。"},
            {"name": "四草綠色隧道", "category": "自然生態", "description": "台灣袖珍版亞馬遜。"}
        ]
    }
    
    # 預設資料池
    pool = mock_db.get(destination[:2], [
        {"name": f"{destination}老街", "category": "歷史人文", "description": "在地特色街道。"},
        {"name": f"{destination}夜市", "category": "在地美食", "description": "在地小吃聚集地。"},
        {"name": f"{destination}公園", "category": "自然生態", "description": "放鬆身心的好去處。"}
    ])
    
    # 資料不夠就複製湊數
    if len(pool) < days * 2:
        pool = pool * 5

    selected_spots = []
    
    for i in range(1, days + 1):
        # 每天隨機挑 2 個
        daily = random.sample(pool, 2)
        for spot in daily:
            selected_spots.append({
                "day": i,
                "name": spot["name"],
                "description": spot["description"],
                "category": spot["category"]
            })

    return {
        "title": f"🤖 {destination} {style} 智慧之旅",
        "spots": selected_spots
    }

@router.post("/generate_itinerary")
def generate_itinerary_by_ai(request: AIPlanRequest, db: Session = Depends(get_db)):
    print(f"收到請求: {request}")
    ai_data = None

    # 1. 嘗試呼叫真 AI (失敗會自動去 Mock)
    try:
        model = genai.GenerativeModel('gemini-pro') 
        prompt = f"""
        你是一個旅遊規劃師。請幫我規劃行程，直接輸出純 JSON。
        需求：地點 {request.destination}，{request.days}天，風格{request.style}，預算{request.budget}。
        格式：{{ "title": "名稱", "spots": [ {{ "day": 1, "name": "景點", "description": "簡介", "category": "分類" }} ] }}
        """
        response = model.generate_content(prompt)
        content = response.text.replace("```json", "").replace("```", "").strip()
        ai_data = json.loads(content)
        print("✅ Google AI 生成成功")

    except Exception as e:
        print(f"❌ AI 呼叫失敗 ({e})，切換至 Mock 模式")
        ai_data = get_mock_itinerary(request.destination, request.days, request.style)

    # 2. 寫入資料庫
    try:
        new_itinerary_id = str(uuid.uuid4())
        code = new_itinerary_id[:8].upper()
        
        new_itinerary = models.Itinerary(
            id=new_itinerary_id,
            code=code,
            title=ai_data['title'],
            budget=request.budget,
            owner_user_id=request.owner_id,
            travel_time=f"{request.days} 天",
            transport="AI 推薦",
            lodging="AI 推薦"
        )
        db.add(new_itinerary)
        db.flush()

        for index, item in enumerate(ai_data['spots']):
            spot_name = item['name']
            existing_spot = db.query(models.Spot).filter(models.Spot.name == spot_name).first()
            
            spot_id_to_use = ""
            if existing_spot:
                spot_id_to_use = existing_spot.id
            else:
                new_spot_id = str(uuid.uuid4())
                new_spot = models.Spot(
                    id=new_spot_id,
                    name=spot_name,
                    category=item.get('category', '其他'),
                    location=request.destination,
                    features={"description": item.get('description', '')},
                    description=item.get('description', '')
                )
                db.add(new_spot)
                db.flush()
                spot_id_to_use = new_spot_id
            
            link = models.ItinerarySpot(
                itinerary_id=new_itinerary_id,
                spot_id=spot_id_to_use,
                day_order=index,
                note=f"第 {item.get('day', 1)} 天: {item.get('description', '')}"
            )
            db.add(link)

        db.commit()
        return {"itinerary_id": new_itinerary_id, "message": "行程規劃完成！"}

    except Exception as e:
        db.rollback()
        print(f"DB Error: {e}") 
        raise HTTPException(status_code=500, detail="寫入資料庫失敗")