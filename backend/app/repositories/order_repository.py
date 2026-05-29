"""Order repository."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException, ValidationException
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.order import OrderSearchParams

ALLOWED_STATUS_TRANSITIONS: dict[str, list[str]] = {
    "pending": ["confirmed", "cancelled"],
    "confirmed": ["shipping", "cancelled"],
    "shipping": ["delivered", "cancelled"],
    "delivered": [],
    "cancelled": [],
}


class OrderRepository:
    """Data access layer for orders."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_with_items(
        self,
        order_data: dict[str, Any],
        items: list[dict[str, Any]],
        session: AsyncSession | None = None,
    ) -> Order:
        """Create an order and line items in the active transaction."""
        active_session = session or self.session
        order_data.setdefault(
            "order_number",
            f"GB-{datetime.now(UTC):%Y%m%d}-{uuid4().hex[:4].upper()}",
        )
        order = Order(**order_data)
        active_session.add(order)
        await active_session.flush()
        for item_data in items:
            active_session.add(OrderItem(order_id=order.id, **item_data))
        await active_session.flush()
        await active_session.refresh(order, attribute_names=["items"])
        return order

    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Find order by ID with items."""
        result = await self.session.execute(
            select(Order).where(Order.id == order_id).options(selectinload(Order.items))
        )
        return result.scalar_one_or_none()

    async def get_by_order_number(self, order_number: str) -> Order | None:
        """Find order by order number."""
        result = await self.session.execute(
            select(Order)
            .where(Order.order_number == order_number)
            .options(selectinload(Order.items))
        )
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(self, key: UUID) -> Order | None:
        """Find order by idempotency key."""
        result = await self.session.execute(
            select(Order).where(Order.idempotency_key == key).options(selectinload(Order.items))
        )
        return result.scalar_one_or_none()

    async def get_by_order_number_and_phone(self, order_number: str, phone: str) -> Order | None:
        """Find order by order number and customer phone."""
        result = await self.session.execute(
            select(Order)
            .where(Order.order_number == order_number, Order.customer_phone == phone)
            .options(selectinload(Order.items))
        )
        return result.scalar_one_or_none()

    async def list_user_orders(
        self,
        user_id: UUID,
        params: OrderSearchParams,
    ) -> tuple[list[Order], int]:
        """List orders for a user."""
        query = select(Order).where(Order.user_id == user_id)
        return await self._list(query, params)

    async def list_orders_by_phone(
        self,
        phone: str,
        params: OrderSearchParams,
    ) -> tuple[list[Order], int]:
        """List orders matching customer phone or registered user phone."""
        query = (
            select(Order)
            .outerjoin(User, Order.user_id == User.id)
            .where(or_(Order.customer_phone == phone, User.phone == phone))
        )
        return await self._list(query, params)

    async def list_all_orders(self, params: OrderSearchParams) -> tuple[list[Order], int]:
        """List orders for admin."""
        return await self._list(select(Order), params)

    async def update_status(
        self,
        order_id: UUID,
        new_status: str,
        notes: str | None = None,
    ) -> Order:
        """Update order status using allowed transitions."""
        order = await self.get_by_id(order_id)
        if not order:
            raise NotFoundException("Order not found", error_code="order_not_found")
        allowed = ALLOWED_STATUS_TRANSITIONS[order.status]
        if new_status not in allowed:
            raise ValidationException(
                f"Cannot transition order from {order.status} to {new_status}",
                error_code="invalid_status_transition",
            )
        order.status = new_status
        if notes:
            order.internal_notes = notes
        now = datetime.now(UTC)
        if new_status == "delivered":
            order.delivered_at = now
        if new_status == "cancelled":
            order.cancelled_at = now
            order.cancelled_reason = notes
        await self.session.flush()
        await self.session.refresh(order, attribute_names=["items"])
        return order

    async def cancel_order(self, order_id: UUID, reason: str | None = None) -> Order:
        """Cancel an order when its current status allows it."""
        return await self.update_status(order_id, "cancelled", reason)

    async def _list(
        self,
        query: Select[tuple[Order]],
        params: OrderSearchParams,
    ) -> tuple[list[Order], int]:
        if params.status:
            query = query.where(Order.status == params.status)
        if params.source:
            query = query.where(Order.source == params.source)
        if params.search:
            term = f"%{params.search.strip()}%"
            query = query.where(
                or_(
                    Order.order_number.ilike(term),
                    Order.customer_name.ilike(term),
                    Order.customer_phone.ilike(term),
                )
            )

        count_query = select(func.count()).select_from(query.order_by(None).subquery())
        total = (await self.session.execute(count_query)).scalar_one()
        result = await self.session.execute(
            query.options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
            .offset(params.skip)
            .limit(params.limit)
        )
        return list(result.scalars().unique().all()), total
