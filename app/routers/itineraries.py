from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database import get_db
from .. import models, schemas
from ..utils import gen_uuid

router = APIRouter(prefix="/itineraries", tags=["itineraries"])

@router.get("/", response_model=List[schemas.ItineraryOut])
def list_itineraries(
    q: str = Query("", description="關鍵字"),
    budget_lte: int | None = Query(None, description="最大預算"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Itinerary).options(
        joinedload(models.Itinerary.spots).joinedload(models.ItinerarySpot.spot)
    )
    if q:
        like = f"%{q}%"
        query = query.filter(
            (models.Itinerary.title.like(like)) |
            (models.Itinerary.transport.like(like))
        )
    if budget_lte is not None:
        query = query.filter(models.Itinerary.budget <= budget_lte)

    items = query.order_by(models.Itinerary.created_at.desc()).all()
    result: List[schemas.ItineraryOut] = []
    for it in items:
        spots = [schemas.SpotOut.model_validate(is_rel.spot) for is_rel in it.spots]
        result.append(
            schemas.ItineraryOut(
                id=it.id,
                code=it.code,
                title=it.title,
                budget=it.budget,
                travel_time=it.travel_time,
                lodging=it.lodging,
                transport=it.transport,
                owner_user_id=it.owner_user_id,
                created_at=it.created_at,
                spots=spots,
            )
        )
    return result

@router.get("/{itinerary_id}", response_model=schemas.ItineraryOut)
def get_itinerary(itinerary_id: str, db: Session = Depends(get_db)):
    it = db.query(models.Itinerary).options(
        joinedload(models.Itinerary.spots).joinedload(models.ItinerarySpot.spot)
    ).filter(models.Itinerary.id == itinerary_id).first()
    if not it:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    spots = [schemas.SpotOut.model_validate(is_rel.spot) for is_rel in it.spots]
    return schemas.ItineraryOut(
        id=it.id,
        code=it.code,
        title=it.title,
        budget=it.budget,
        travel_time=it.travel_time,
        lodging=it.lodging,
        transport=it.transport,
        owner_user_id=it.owner_user_id,
        created_at=it.created_at,
        spots=spots,
    )

@router.post("/", response_model=schemas.ItineraryOut, status_code=201)
def create_itinerary(payload: schemas.ItineraryCreate, db: Session = Depends(get_db)):
    # basic owner check: ensure user exists
    owner = db.query(models.User).filter_by(id=payload.owner_user_id).first()
    if not owner:
        raise HTTPException(status_code=400, detail="Owner user not found")

    itinerary_id = gen_uuid()
    code = f"TRIP-{itinerary_id[:8].upper()}"
    it = models.Itinerary(
        id=itinerary_id,
        code=code,
        title=payload.title,
        budget=payload.budget,
        travel_time=payload.travel_time,
        lodging=payload.lodging,
        transport=payload.transport,
        owner_user_id=payload.owner_user_id,
    )
    db.add(it)
    db.flush()

    for sid in payload.spot_ids:
        db.add(models.ItinerarySpot(itinerary_id=it.id, spot_id=sid))

    db.commit()
    db.refresh(it)

    # load spots
    db.refresh(it)
    it = db.query(models.Itinerary).options(
        joinedload(models.Itinerary.spots).joinedload(models.ItinerarySpot.spot)
    ).get(it.id)
    spots = [schemas.SpotOut.model_validate(is_rel.spot) for is_rel in it.spots]
    return schemas.ItineraryOut(
        id=it.id,
        code=it.code,
        title=it.title,
        budget=it.budget,
        travel_time=it.travel_time,
        lodging=it.lodging,
        transport=it.transport,
        owner_user_id=it.owner_user_id,
        created_at=it.created_at,
        spots=spots,
    )
