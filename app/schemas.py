from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

# ----- User -----

class UserBase(BaseModel):
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(min_length=4)

class UserOut(UserBase):
    id: str
    created_at: datetime

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

class ItinerarySpotInfo(BaseModel):
    spot_id: str
    day_order: Optional[int] = None
    note: Optional[str] = None

    class Config:
        from_attributes = True

class ItineraryOut(ItineraryBase):
    id: str
    code: str
    owner_user_id: str
    created_at: datetime
    spots: List[SpotOut] = []

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
