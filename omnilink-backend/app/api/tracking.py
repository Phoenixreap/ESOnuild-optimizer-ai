from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import AffiliateProfile, Click, Product


router = APIRouter(prefix="/t", tags=["tracking"])


@router.get("/{product_id}")
def track_and_redirect(product_id: int, request: Request, affiliate_id: int | None = None, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Product not found")
    affiliate: AffiliateProfile | None = db.get(AffiliateProfile, affiliate_id) if affiliate_id else None
    click = Click(
        product_id=product.id,
        affiliate_id=affiliate.id if affiliate else None,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(click)
    db.commit()
    return RedirectResponse(url=product.sales_page_url, status_code=302)

