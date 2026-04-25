from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import Base, engine, SessionLocal
from .seed_data import seed
from .routers import health, spots, itineraries, reviews, travel_records, users, auth, ai_plan, collab, expenses

# 建表
Base.metadata.create_all(bind=engine)

# 種子資料（只在第一次有空資料時執行）
with SessionLocal() as db:
    seed(db)

app = FastAPI(title="Travel Backend (FastAPI + MySQL)")

# 加上這段，讓根目錄 / 有東西可以回傳
@app.get("/")
def read_root():
    return {"message": "恭喜！前端成功連上後端了！"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routers
app.include_router(health.router,prefix="/api/health")
app.include_router(spots.router,prefix="/api/spots")
app.include_router(itineraries.router, prefix="/api/itineraries")
app.include_router(reviews.router, prefix="/api/reviews")
app.include_router(travel_records.router, prefix="/api/travel-records")
app.include_router(users.router, prefix="/api/users")
app.include_router(auth.router,prefix="/auth")
app.include_router(ai_plan.router, prefix="/api/ai-plan")
app.include_router(collab.router, prefix="/api/collab")
app.include_router(expenses.router, prefix="/api/expenses")