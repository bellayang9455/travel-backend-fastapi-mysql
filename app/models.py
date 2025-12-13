from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timedelta
from .database import Base

def taiwan_time():
    return datetime.utcnow() + timedelta(hours=8)

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(190), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(30))
    birthday: Mapped[datetime | None] = mapped_column(DateTime)
    likes: Mapped[dict | None] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=taiwan_time)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=taiwan_time, onupdate=taiwan_time)

    itineraries: Mapped[list["Itinerary"]] = relationship(back_populates="owner")
    reviews: Mapped[list["Review"]] = relationship(back_populates="user")
    travel_records: Mapped[list["TravelRecord"]] = relationship(back_populates="user")


class Itinerary(Base):
    __tablename__ = "itineraries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    budget: Mapped[int | None] = mapped_column(Integer)
    travel_time: Mapped[str | None] = mapped_column(String(100))
    lodging: Mapped[str | None] = mapped_column(String(100))
    transport: Mapped[str | None] = mapped_column(String(100))

    owner_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    owner: Mapped["User"] = relationship(back_populates="itineraries")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=taiwan_time)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=taiwan_time, onupdate=taiwan_time)

    spots: Mapped[list["ItinerarySpot"]] = relationship(back_populates="itinerary", cascade="all, delete-orphan")
    travel_records: Mapped[list["TravelRecord"]] = relationship(back_populates="itinerary", cascade="all, delete-orphan")


class Spot(Base):
    __tablename__ = "spots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100))
    features: Mapped[dict | None] = mapped_column(JSON)
    location: Mapped[str | None] = mapped_column(String(100))
    hours: Mapped[str | None] = mapped_column(String(100))
    activities: Mapped[dict | None] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reviews: Mapped[list["Review"]] = relationship(back_populates="spot")
    in_plans: Mapped[list["ItinerarySpot"]] = relationship(back_populates="spot", cascade="all, delete-orphan")


class ItinerarySpot(Base):
    __tablename__ = "itinerary_spots"

    itinerary_id: Mapped[str] = mapped_column(String(36), ForeignKey("itineraries.id"), primary_key=True)
    spot_id: Mapped[str] = mapped_column(String(36), ForeignKey("spots.id"), primary_key=True)
    day_order: Mapped[int | None] = mapped_column(Integer)
    note: Mapped[str | None] = mapped_column(String(255))

    itinerary: Mapped["Itinerary"] = relationship(back_populates="spots")
    spot: Mapped["Spot"] = relationship(back_populates="in_plans")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    spot_id: Mapped[str] = mapped_column(String(36), ForeignKey("spots.id"), nullable=False)
    stars: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str | None] = mapped_column(Text)
    photos: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="reviews")
    spot: Mapped["Spot"] = relationship(back_populates="reviews")


class TravelRecord(Base):
    __tablename__ = "travel_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    itinerary_id: Mapped[str] = mapped_column(String(36), ForeignKey("itineraries.id"), nullable=False)
    experience: Mapped[str | None] = mapped_column(Text)
    cost_ticket: Mapped[int | None] = mapped_column(Integer)
    cost_lodging: Mapped[int | None] = mapped_column(Integer)
    cost_food: Mapped[int | None] = mapped_column(Integer)
    cost_transport: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="travel_records")
    itinerary: Mapped["Itinerary"] = relationship(back_populates="travel_records")
