from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas
from ..utils import gen_uuid

router = APIRouter(prefix="/spots", tags=["spots"])

@router.get("/", response_model=List[schemas.SpotOut])
def list_spots(q: str = Query("", description="關鍵字"), db: Session = Depends(get_db)):
    query = db.query(models.Spot)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (models.Spot.name.like(like)) |
            (models.Spot.location.like(like)) |
            (models.Spot.category.like(like))
        )
    spots = query.order_by(models.Spot.created_at.desc()).all()
    return spots

@router.post("/", response_model=schemas.SpotOut, status_code=201)
def create_spot(payload: schemas.SpotCreate, db: Session = Depends(get_db)):
    spot = models.Spot(
        id=gen_uuid(),
        name=payload.name,
        category=payload.category,
        features=payload.features,
        location=payload.location,
        hours=payload.hours,
        activities=payload.activities,
    )
    db.add(spot)
    db.commit()
    db.refresh(spot)
    return spot
