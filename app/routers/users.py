from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import User  # Assuming the User model is in .models
from ..database import get_db  # Assuming you have a get_db dependency
from ..schemas import UserOut, UserUpdate # Assuming Pydantic models are in .schemas

router = APIRouter(prefix="/users", tags=["users"])

# 1. GET User by ID
@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Retrieves a specific user by their ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# 2. PUT (Update) User
@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Updates user information."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields from the request
    # This example only updates fields that are actually provided (exclude_unset=True)
    update_data = user_update.dict(exclude_unset=True) 
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user