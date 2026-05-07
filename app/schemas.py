from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

# -- User --
class UserBase(BaseModel):
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    birthday: Optional[datetime] = None
    likes: Optional[Any] = None

class UserCreate(UserBase):
    password: str = Field(min_length=4)
    
class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    birthday: Optional[datetime] = None
    likes: Optional[Any] = None
    password: Optional[str] = Field(None, min_length=4)

class UserOut(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserBasic(BaseModel):
    id: str
    name: Optional[str] = None
    email: str

    class Config:
        from_attributes = True

# -- Spot --
class SpotBase(BaseModel):
    name: str
    category: Optional[str] = None
    features: Optional[Any] = None
    location: Optional[str] = None
    hours: Optional[str] = None
    activities: Optional[Any] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class SpotCreate(SpotBase):
    pass

class SpotOut(SpotBase):
    id: str
    created_at: datetime
    region: Optional[str] = None
    avg_rating: float = 0.0
    review_count: int = 0

    class Config:
        from_attributes = True

# -- Itinerary --
class ItineraryBase(BaseModel):
    title: str
    budget: Optional[int] = None
    travel_time: Optional[str] = None
    transport: Optional[str] = None

class ItineraryCreate(ItineraryBase):
    owner_user_id: str
    spot_ids: List[str] = []

class ItineraryItemUpdate(BaseModel):
    item_id: int
    new_day_order: int
    new_order: int

class ItinerarySpotOut(BaseModel):
    id : int
    day_order: int
    note: Optional[str] = None
    spot: SpotOut

    class Config:
        from_attributes = True

class ItineraryOut(ItineraryBase):
    id: str
    code: str
    owner_user_id: str
    created_at: datetime
    spots: List[ItinerarySpotOut] = []
    owner: Optional[UserBasic] = None        # 房主資訊
    collaborators: List[UserBasic] = []  # 協作者資訊

    class Config:
        from_attributes = True


# -- Review --
class ReviewBase(BaseModel):
    stars: int
    content: Optional[str] = None
    photos: Optional[Any] = None

class ReviewCreate(ReviewBase):
    user_id: str
    spot_id: str

class ReviewOut(ReviewBase):
    id: str
    user_id: str
    spot_id: str
    created_at: datetime
    user_name: Optional[str] = None

    class Config:
        from_attributes = True


# -- TravelRecord --
class TravelRecordBase(BaseModel):
    experience: Optional[str] = None
    cost_ticket: Optional[int] = None
    cost_lodging: Optional[int] = None
    cost_food: Optional[int] = None
    cost_transport: Optional[int] = None

class TravelRecordCreate(TravelRecordBase):
    user_id: str
    itinerary_id: str

class TravelRecordOut(TravelRecordBase):
    id: str
    user_id: str
    itinerary_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# -- AccountingRecord --
class SplitDetail(BaseModel):
    user_id: str
    amount: float

# 花費 (Expense) 的基礎模型
class ExpenseBase(BaseModel):
    itinerary_id: str       # 屬於哪個行程
    payer_id: str           # 誰付的錢
    description: str        # 買了什麼 (例如: 高鐵票)
    amount: float           # 總金額
    currency: Optional[str] = "TWD"
    split_details: List[SplitDetail]  # 規定須傳入 List 格式

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseOut(ExpenseBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True