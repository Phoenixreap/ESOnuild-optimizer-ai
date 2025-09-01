from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.models import AffiliateProfile, AffiliateSelection, Product, User, UserRole
from app.schemas.schemas import ProductOut


router = APIRouter(prefix="/affiliate", tags=["affiliate"])


def require_affiliate(user: User) -> None:
    if user.role != UserRole.AFFILIATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Affiliate role required")


@router.get("/marketplace", response_model=list[ProductOut])
def list_marketplace(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_active == True).order_by(Product.created_at.desc()).all()  # noqa: E712
    return products


@router.post("/select/{product_id}")
def select_product(product_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_affiliate(user)
    affiliate: AffiliateProfile | None = user.affiliate_profile
    if not affiliate:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Affiliate profile missing")
    product = db.get(Product, product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    existing = db.query(AffiliateSelection).filter(
        AffiliateSelection.affiliate_id == affiliate.id,
        AffiliateSelection.product_id == product.id,
    ).first()
    if existing:
        return {"status": "already_selected"}
    selection = AffiliateSelection(affiliate_id=affiliate.id, product_id=product.id)
    db.add(selection)
    db.commit()
    return {"status": "selected"}


@router.get("/selections", response_model=list[ProductOut])
def my_selected_products(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    require_affiliate(user)
    affiliate = user.affiliate_profile
    selections = db.query(AffiliateSelection).filter(AffiliateSelection.affiliate_id == affiliate.id).all()
    products = [s.product for s in selections]
    return products

