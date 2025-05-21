from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models import Company, User
from app.core.schemas import Company as CompanySchema
from app.core.schemas import CompanyCreate, CompanyUpdate
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[CompanySchema])
def read_companies(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve companies.
    """
    companies = db.query(Company).offset(skip).limit(limit).all()
    return companies

@router.post("/", response_model=CompanySchema)
def create_company(
    *,
    db: Session = Depends(get_db),
    company_in: CompanyCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new company.
    """
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    company = db.query(Company).filter(Company.id == company_in.id).first()
    if company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this tax code already exists"
        )
    company = Company(**company_in.dict())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@router.put("/{company_id}", response_model=CompanySchema)
def update_company(
    *,
    db: Session = Depends(get_db),
    company_id: str,
    company_in: CompanyUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update a company.
    """
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    for field, value in company_in.dict(exclude_unset=True).items():
        setattr(company, field, value)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@router.delete("/{company_id}", response_model=CompanySchema)
def delete_company(
    *,
    db: Session = Depends(get_db),
    company_id: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Delete a company.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    db.delete(company)
    db.commit()
    return company 