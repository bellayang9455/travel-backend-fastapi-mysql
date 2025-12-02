# Travel Backend (FastAPI + MySQL)

後端專案，語言為 **Python (FastAPI)**，資料庫使用 **MySQL**，對應你的 ERD：
- 使用者 (User)
- 行程 (Itinerary)
- 景點 (Spot)
- 行程×景點 (ItinerarySpot, M:N)
- 評價 (Review)
- 旅遊紀錄 (TravelRecord)

## 快速啟動

```bash
# 1. 啟動 MySQL (使用 Docker)
docker compose up -d

# 2. 安裝依賴
python -m venv .venv
source .venv/bin/activate  # Windows 使用: .venv\Scripts\activate
pip install -r requirements.txt

# 3. 建立 .env
cp .env.example .env       # Windows 可用: copy .env.example .env

# 4. 第一次啟動會自動建表並執行種子資料
uvicorn app.main:app --reload
```

啟動後：
- API 入口： http://localhost:8000
- Docs： http://localhost:8000/docs

## 主要 API

- `GET /health`
- `GET /spots`、`POST /spots`
- `GET /itineraries`、`GET /itineraries/{itinerary_id}`、`POST /itineraries`
- `GET /reviews`、`POST /reviews`
- `POST /travel-records`
