from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database import get_db
from .. import models, schemas
from ..utils import gen_uuid

router = APIRouter(tags=["reviews"])

@router.get("/", response_model=List[schemas.ReviewOut])
def list_reviews(
    spot_id: str | None = Query(None, description="景點 ID"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Review).options(joinedload(models.Review.user))
    if spot_id:
        query = query.filter(models.Review.spot_id == spot_id)
    items = query.order_by(models.Review.created_at.desc()).all()
    result: List[schemas.ReviewOut] = []
    for r in items:
        result.append(
            schemas.ReviewOut(
                id=r.id,
                user_id=r.user_id,
                spot_id=r.spot_id,
                stars=r.stars,
                content=r.content,
                photos=r.photos,
                created_at=r.created_at,
                user_name=r.user.name if r.user else None,
            )
        )
    return result

@router.post("/", response_model=schemas.ReviewOut, status_code=201)
def create_review(payload: schemas.ReviewCreate, db: Session = Depends(get_db)):
    # simple existence checks
    user = db.query(models.User).filter_by(id=payload.user_id).first()
    spot = db.query(models.Spot).filter_by(id=payload.spot_id).first()
    if not user or not spot:
        raise HTTPException(status_code=400, detail="User or spot not found")

    r = models.Review(
        id=gen_uuid(),
        user_id=payload.user_id,
        spot_id=payload.spot_id,
        stars=payload.stars,
        content=payload.content,
        photos=payload.photos,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return schemas.ReviewOut(
        id=r.id,
        user_id=r.user_id,
        spot_id=r.spot_id,
        stars=r.stars,
        content=r.content,
        photos=r.photos,
        created_at=r.created_at,
        user_name=user.name,
    )
