from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.business import Business
from app.schemas.business import BusinessCreate, BusinessResponse
from sqlalchemy import desc

router = APIRouter()

@router.get("/most-requested", response_model=List[BusinessResponse])
def get_most_requested_businesses(db: Session = Depends(get_db)):
    businesses = db.query(Business).order_by(desc(Business.view_count)).limit(10).all()
    return businesses

@router.get("/last-added", response_model=List[BusinessResponse])
def get_last_added_businesses(db: Session = Depends(get_db)):
    businesses = db.query(Business).order_by(desc(Business.created_at)).limit(10).all()
    return businesses

@router.post("/", response_model=BusinessResponse)
def create_business(business: BusinessCreate, db: Session = Depends(get_db)):
    db_business = Business(**business.dict())
    db.add(db_business)
    db.commit()
    db.refresh(db_business)
    return db_business

@router.get("/{business_id}", response_model=BusinessResponse)
def get_business(business_id: int, db: Session = Depends(get_db)):
    business = db.query(Business).filter(Business.id == business_id).first()
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Increment view count
    business.view_count += 1
    db.commit()
    db.refresh(business)
    
    return business 