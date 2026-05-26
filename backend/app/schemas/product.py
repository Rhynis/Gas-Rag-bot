"""Product schemas."""

import re
from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

ALLOWED_SIZES = {Decimal("6"), Decimal("12"), Decimal("45")}
SKU_PATTERN = re.compile(r"^[A-Z0-9-]+$")


def validate_size(value: Decimal | None) -> Decimal | None:
    """Validate supported LPG cylinder sizes."""
    if value is not None and value not in ALLOWED_SIZES:
        raise ValueError("size_kg must be one of 6, 12, or 45")
    return value


class ProductBase(BaseModel):
    """Shared product fields."""

    name: str = Field(min_length=1, max_length=255)
    brand: str = Field(min_length=1, max_length=100)
    size_kg: Decimal
    price: Decimal = Field(gt=0)
    description: str | None = None
    image_url: HttpUrl | None = None
    safety_info: str | None = None

    @field_validator("size_kg")
    @classmethod
    def validate_size_kg(cls, value: Decimal) -> Decimal:
        return validate_size(value) or value


class ProductCreate(ProductBase):
    """Product creation payload."""

    sku: str = Field(min_length=1, max_length=50)
    stock_quantity: int = Field(ge=0)

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str) -> str:
        normalized = value.upper().strip()
        if not SKU_PATTERN.match(normalized):
            raise ValueError("sku must contain only uppercase letters, numbers, and dashes")
        return normalized


class ProductUpdate(BaseModel):
    """Product update payload."""

    sku: str | None = Field(default=None, min_length=1, max_length=50)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    brand: str | None = Field(default=None, min_length=1, max_length=100)
    size_kg: Decimal | None = None
    price: Decimal | None = Field(default=None, gt=0)
    description: str | None = None
    image_url: HttpUrl | None = None
    safety_info: str | None = None
    stock_quantity: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

    @field_validator("size_kg")
    @classmethod
    def validate_size_kg(cls, value: Decimal | None) -> Decimal | None:
        return validate_size(value)

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.upper().strip()
        if not SKU_PATTERN.match(normalized):
            raise ValueError("sku must contain only uppercase letters, numbers, and dashes")
        return normalized


class ProductResponse(ProductCreate):
    """Product API response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    """Paginated product list response."""

    items: list[ProductResponse]
    total: int
    page: int
    limit: int
    has_more: bool


class ProductSearchParams(BaseModel):
    """Product search and filter parameters."""

    search: str | None = Field(default=None, max_length=255)
    brand: str | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    size_kg: Decimal | None = None
    in_stock_only: bool = False
    sort_by: Literal["created_at", "price", "name"] = "created_at"
    sort_order: Literal["asc", "desc"] = "desc"
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)

    @field_validator("size_kg")
    @classmethod
    def validate_size_kg(cls, value: Decimal | None) -> Decimal | None:
        return validate_size(value)

    @model_validator(mode="after")
    def validate_price_range(self) -> "ProductSearchParams":
        """Validate min/max price relationship."""
        if (
            self.min_price is not None
            and self.max_price is not None
            and self.min_price > self.max_price
        ):
            raise ValueError("min_price must be less than or equal to max_price")
        return self
