from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.models import Product, User, UserRole
from app.schemas.schemas import ProductCreate, ProductOut


router = APIRouter(prefix="/business", tags=["business"])


def require_business(user: User) -> None:
    if user.role != UserRole.BUSINESS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Business role required")


@router.post("/products", response_model=ProductOut)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_business(user)
    business_profile = user.business_profile
    if not business_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Business profile missing")
    product = Product(
        business_id=business_profile.id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        sales_page_url=str(payload.sales_page_url),
        affiliate_commission_percent=payload.affiliate_commission_percent,
        image_url=str(payload.image_url) if payload.image_url else None,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/products", response_model=list[ProductOut])
def list_my_products(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_business(user)
    business_profile = user.business_profile
    products = db.query(Product).filter(Product.business_id == business_profile.id).order_by(Product.created_at.desc()).all()
    return products

