from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.models import User, Organization
from backend.schemas.schemas import UserResponse, OrganizationResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/demo-login", response_model=UserResponse)
def demo_login(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == "demo@bizmind.kz").first()
    if not user:
        # Fallback query
        user = db.query(User).first()
    return user

@router.get("/me", response_model=UserResponse)
def get_current_user(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == "demo@bizmind.kz").first()
    if not user:
        user = db.query(User).first()
    return user
