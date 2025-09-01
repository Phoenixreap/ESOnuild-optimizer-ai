from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class UserRole(str, Enum):
    BUSINESS = "BUSINESS"
    AFFILIATE = "AFFILIATE"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    business_profile: Mapped["BusinessProfile"] = relationship(back_populates="user", uselist=False)
    affiliate_profile: Mapped["AffiliateProfile"] = relationship(back_populates="user", uselist=False)


class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    website_url: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship(back_populates="business_profile")
    products: Mapped[list["Product"]] = relationship(back_populates="business")


class AffiliateProfile(Base):
    __tablename__ = "affiliate_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship(back_populates="affiliate_profile")
    selections: Mapped[list["AffiliateSelection"]] = relationship(back_populates="affiliate")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("business_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text())
    price: Mapped[float] = mapped_column(Float, nullable=False)
    sales_page_url: Mapped[str] = mapped_column(String(512), nullable=False)
    affiliate_commission_percent: Mapped[float] = mapped_column(Float, nullable=False)  # 0-100
    image_url: Mapped[str | None] = mapped_column(String(512))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    business: Mapped[BusinessProfile] = relationship(back_populates="products")
    selections: Mapped[list["AffiliateSelection"]] = relationship(back_populates="product")
    clicks: Mapped[list["Click"]] = relationship(back_populates="product")
    sales: Mapped[list["Sale"]] = relationship(back_populates="product")

    __table_args__ = (
        CheckConstraint("affiliate_commission_percent >= 0 AND affiliate_commission_percent <= 100", name="ck_commission_range"),
    )


class AffiliateSelection(Base):
    __tablename__ = "affiliate_selections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    affiliate_id: Mapped[int] = mapped_column(ForeignKey("affiliate_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    affiliate: Mapped[AffiliateProfile] = relationship(back_populates="selections")
    product: Mapped[Product] = relationship(back_populates="selections")

    __table_args__ = (
        UniqueConstraint("affiliate_id", "product_id", name="uq_affiliate_product"),
    )


class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)
    affiliate_id: Mapped[int | None] = mapped_column(ForeignKey("affiliate_profiles.id", ondelete="SET NULL"))
    ip_address: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    product: Mapped[Product] = relationship(back_populates="clicks")


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)
    affiliate_id: Mapped[int | None] = mapped_column(ForeignKey("affiliate_profiles.id", ondelete="SET NULL"))
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[Numeric] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    gross_amount: Mapped[Numeric] = mapped_column(Numeric(12, 2), nullable=False)
    affiliate_commission_amount: Mapped[Numeric] = mapped_column(Numeric(12, 2), nullable=False)
    platform_fee_amount: Mapped[Numeric] = mapped_column(Numeric(12, 2), nullable=False)
    business_revenue_amount: Mapped[Numeric] = mapped_column(Numeric(12, 2), nullable=False)
    external_order_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    product: Mapped[Product] = relationship(back_populates="sales")


class Payout(Base):
    __tablename__ = "payouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    affiliate_id: Mapped[int] = mapped_column(ForeignKey("affiliate_profiles.id", ondelete="CASCADE"), index=True, nullable=False)
    amount: Mapped[Numeric] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    note: Mapped[str | None] = mapped_column(String(255))

