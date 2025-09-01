from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import User, UserRole
from app.schemas.schemas import UserCreate, UserOut
from app.services.security import hash_password


from app.api.auth import router as auth_router
from app.api.business import router as business_router
from app.api.affiliate import router as affiliate_router
from app.api.tracking import router as tracking_router
from app.api.sales import router as sales_router
from app.api.dashboard import router as dashboard_router


router = APIRouter()


@router.post("/signup", response_model=UserOut)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(email=payload.email, hashed_password=hash_password(payload.password), role=payload.role)
    db.add(user)
    db.flush()

    if payload.role == UserRole.BUSINESS:
        from app.models.models import BusinessProfile

        profile = BusinessProfile(user_id=user.id, display_name=payload.display_name, website_url=payload.website_url)
        db.add(profile)
    else:
        from app.models.models import AffiliateProfile

        profile = AffiliateProfile(user_id=user.id, display_name=payload.display_name)
        db.add(profile)

    db.commit()
    db.refresh(user)
    return user


# Mount sub-routers
router.include_router(auth_router)
router.include_router(business_router)
router.include_router(affiliate_router)
router.include_router(tracking_router)
router.include_router(sales_router)
router.include_router(dashboard_router)

