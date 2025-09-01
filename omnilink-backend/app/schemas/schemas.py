from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl, field_validator


class UserRole(str, Enum):
    BUSINESS = "BUSINESS"
    AFFILIATE = "AFFILIATE"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole
    display_name: str
    website_url: Optional[HttpUrl] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    sales_page_url: HttpUrl
    affiliate_commission_percent: float
    image_url: Optional[HttpUrl] = None


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int
    business_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

