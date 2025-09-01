from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.models import AffiliateProfile, Product, Sale, User, UserRole


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/affiliate")
def affiliate_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != UserRole.AFFILIATE:
        return {"error": "Affiliate role required"}
    affiliate: AffiliateProfile | None = user.affiliate_profile
    if not affiliate:
        return {"error": "Affiliate profile missing"}
    sales = (
        db.query(
            func.count(Sale.id),
            func.coalesce(func.sum(Sale.gross_amount), 0),
            func.coalesce(func.sum(Sale.affiliate_commission_amount), 0),
        )
        .filter(Sale.affiliate_id == affiliate.id)
        .one()
    )
    return {
        "selected_products": len(affiliate.selections),
        "sales_count": int(sales[0] or 0),
        "gross_amount": str(Decimal(sales[1] or 0)),
        "commissions_earned": str(Decimal(sales[2] or 0)),
    }


@router.get("/business")
def business_product_tracker(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != UserRole.BUSINESS:
        return {"error": "Business role required"}
    products = (
        db.query(Product)
        .filter(Product.business_id == user.business_profile.id)
        .all()
    )
    product_ids = [p.id for p in products]
    aggregates = (
        db.query(
            Sale.product_id,
            func.count(Sale.id).label("sales_count"),
            func.coalesce(func.sum(Sale.gross_amount), 0).label("gross"),
            func.coalesce(func.sum(Sale.affiliate_commission_amount), 0).label("affiliate"),
            func.coalesce(func.sum(Sale.platform_fee_amount), 0).label("platform"),
            func.coalesce(func.sum(Sale.business_revenue_amount), 0).label("business"),
        )
        .filter(Sale.product_id.in_(product_ids))
        .group_by(Sale.product_id)
        .all()
        if product_ids
        else []
    )
    agg_by_product = {row.product_id: row for row in aggregates}
    items = []
    for p in products:
        row = agg_by_product.get(p.id)
        items.append(
            {
                "product_id": p.id,
                "name": p.name,
                "sales_count": int(row.sales_count) if row else 0,
                "gross": str(Decimal(row.gross)) if row else "0",
                "affiliate": str(Decimal(row.affiliate)) if row else "0",
                "platform": str(Decimal(row.platform)) if row else "0",
                "business": str(Decimal(row.business)) if row else "0",
            }
        )
    return {"products": items}

