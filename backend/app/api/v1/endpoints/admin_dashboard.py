"""Admin dashboard aggregate endpoints."""

from datetime import UTC, datetime, time
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import get_current_admin
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models.order import Order
from app.models.user import User
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.services.order_service import OrderService
from app.services.product_service import ProductService

router = APIRouter()


class AdminDashboardStats(BaseModel):
    """Top-level admin dashboard metrics."""

    orders_today: int
    orders_pending: int
    revenue_today: int
    low_stock_count: int
    users_total: int
    users_new_today: int


@router.get(
    "/admin/dashboard",
    response_model=AdminDashboardStats,
    summary="Get admin dashboard statistics",
)
@limiter.limit("60/minute")
async def get_admin_dashboard(
    request: Request,
    admin: Annotated[User, Depends(get_current_admin)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AdminDashboardStats:
    """Return aggregate metrics for the admin dashboard."""
    del request
    day_start = datetime.combine(datetime.now(UTC).date(), time.min, tzinfo=UTC)
    day_end = datetime.combine(datetime.now(UTC).date(), time.max, tzinfo=UTC)

    order_service = OrderService(OrderRepository(session), ProductRepository(session))
    order_stats = await order_service.get_statistics(admin)

    product_service = ProductService(ProductRepository(session))
    low_stock_products = await product_service.get_low_stock_products(admin)

    orders_today_statement = (
        select(func.count())
        .select_from(Order)
        .where(
            Order.created_at >= day_start,
            Order.created_at <= day_end,
        )
    )
    revenue_today_statement = select(func.coalesce(func.sum(Order.total_amount), 0)).where(
        Order.created_at >= day_start,
        Order.created_at <= day_end,
        Order.status != "cancelled",
    )
    users_total_statement = select(func.count()).select_from(User)
    users_new_today_statement = (
        select(func.count())
        .select_from(User)
        .where(
            User.created_at >= day_start,
            User.created_at <= day_end,
        )
    )

    orders_today = int((await session.execute(orders_today_statement)).scalar_one())
    revenue_today = int((await session.execute(revenue_today_statement)).scalar_one() or 0)
    users_total = int((await session.execute(users_total_statement)).scalar_one())
    users_new_today = int((await session.execute(users_new_today_statement)).scalar_one())

    return AdminDashboardStats(
        orders_today=orders_today,
        orders_pending=order_stats["pending"],
        revenue_today=revenue_today,
        low_stock_count=len(low_stock_products),
        users_total=users_total,
        users_new_today=users_new_today,
    )
