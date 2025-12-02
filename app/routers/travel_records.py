from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas
from ..utils import gen_uuid

router = APIRouter(prefix="/travel-records", tags=["travel_records"])

@router.post("/", response_model=schemas.TravelRecordOut, status_code=201)
def create_travel_record(payload: schemas.TravelRecordCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(id=payload.user_id).first()
    itinerary = db.query(models.Itinerary).filter_by(id=payload.itinerary_id).first()
    if not user or not itinerary:
        raise HTTPException(status_code=400, detail="User or itinerary not found")

    tr = models.TravelRecord(
        id=gen_uuid(),
        user_id=payload.user_id,
        itinerary_id=payload.itinerary_id,
        experience=payload.experience,
        cost_ticket=payload.cost_ticket,
        cost_lodging=payload.cost_lodging,
        cost_food=payload.cost_food,
        cost_transport=payload.cost_transport,
    )
    db.add(tr)
    db.commit()
    db.refresh(tr)
    return schemas.TravelRecordOut.model_validate(tr)
