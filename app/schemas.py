from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

# ----- User -----

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
# ----- Spot -----

class SpotBase(BaseModel):
    name: str
    category: Optional[str] = None
    features: Optional[Any] = None
    location: Optional[str] = None
    hours: Optional[str] = None
    activities: Optional[Any] = None

class SpotCreate(SpotBase):
    pass

class SpotOut(SpotBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ----- Itinerary -----

class ItineraryBase(BaseModel):
    title: str
    budget: Optional[int] = None
    travel_time: Optional[str] = None
    lodging: Optional[str] = None
    transport: Optional[str] = None

class ItineraryCreate(ItineraryBase):
    owner_user_id: str
    spot_ids: List[str] = []

class ItineraryItemUpdate(BaseModel):
    item_id: int
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


# ----- Review -----

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


# ----- TravelRecord -----

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
