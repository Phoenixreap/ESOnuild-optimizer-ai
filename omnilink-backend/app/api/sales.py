from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.models import AffiliateProfile, Product, Sale


router = APIRouter(prefix="/sales", tags=["sales"])


def calculate_commissions(unit_price: Decimal, quantity: int, affiliate_percent: float) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    gross = (unit_price * Decimal(quantity)).quantize(Decimal("0.01"))
    platform_fee = (gross * Decimal(settings.platform_fee_percent / 100)).quantize(Decimal("0.01"))
    affiliate_commission = (gross * Decimal(affiliate_percent / 100)).quantize(Decimal("0.01"))
    business_revenue = gross - platform_fee - affiliate_commission
    return gross, affiliate_commission, platform_fee, business_revenue


@router.post("")
def record_sale(
    product_id: int,
    quantity: int = 1,
    unit_price: Decimal | None = None,
    currency: str = "USD",
    affiliate_id: int | None = None,
    external_order_id: str | None = None,
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if unit_price is None:
        unit_price = Decimal(str(product.price))
    gross, aff_comm, fee, biz_rev = calculate_commissions(unit_price, quantity, product.affiliate_commission_percent)

    affiliate: AffiliateProfile | None = db.get(AffiliateProfile, affiliate_id) if affiliate_id else None

    sale = Sale(
        product_id=product.id,
        affiliate_id=affiliate.id if affiliate else None,
        quantity=quantity,
        unit_price=unit_price,
        currency=currency,
        gross_amount=gross,
        affiliate_commission_amount=aff_comm,
        platform_fee_amount=fee,
        business_revenue_amount=biz_rev,
        external_order_id=external_order_id,
    )
    db.add(sale)
    db.commit()
    return {
        "status": "recorded",
        "sale_id": sale.id,
        "gross": str(gross),
        "affiliate_commission": str(aff_comm),
        "platform_fee": str(fee),
        "business_revenue": str(biz_rev),
    }

