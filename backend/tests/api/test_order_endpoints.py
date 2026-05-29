"""Tests for order API endpoints."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import get_current_staff, get_current_user_optional
from app.main import app
from app.models.product import Product
from app.models.user import User
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate

pytestmark = pytest.mark.asyncio


def staff_user() -> User:
    now = datetime.now(UTC)
    return User(
        id=uuid4(),
        email="staff@example.com",
        hashed_password="hashed",
        full_name="Staff User",
        phone="+84900000000",
        role="staff",
        is_active=True,
        created_at=now,
        updated_at=now,
    )


def checkout_payload(product: Product) -> dict[str, object]:
    return {
        "items": [{"product_id": str(product.id), "quantity": 1, "is_exchange": False}],
        "customer_name": "Nguyen Van A",
        "customer_phone": "0901234567",
        "customer_email": "customer@example.com",
        "delivery_address": "123 Nguyen Trai",
        "delivery_ward": "Phuong Ben Thanh",
        "delivery_district": "Quan 1",
        "delivery_city": "TP. Hồ Chí Minh",
        "payment_method": "cod",
        "vat_invoice_requested": False,
    }


async def create_db_product(session: AsyncSession, stock_quantity: int = 10) -> Product:
    product = await ProductRepository(session).create(
        ProductCreate(
            sku=f"GAS-{uuid4().hex[:8].upper()}",
            name="Binh gas 12kg",
            brand="Saigon Petro",
            size_kg=Decimal("12"),
            price=Decimal("350000"),
            stock_quantity=stock_quantity,
            description="Binh gas gia dinh",
            image_url="https://example.com/gas-12kg.jpg",
            safety_info="Dat binh noi thoang khi.",
        )
    )
    await session.commit()
    return product


@pytest.fixture
def override_optional_guest() -> object:
    async def guest() -> None:
        return None

    app.dependency_overrides[get_current_user_optional] = guest
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def override_staff() -> object:
    app.dependency_overrides[get_current_staff] = staff_user
    yield
    app.dependency_overrides.clear()


async def test_checkout_without_idempotency_key_returns_422(
    test_client: AsyncClient,
    order_session: AsyncSession,
    override_optional_guest: object,
) -> None:
    product = await create_db_product(order_session)

    response = await test_client.post("/api/v1/orders/checkout", json=checkout_payload(product))

    assert response.status_code == 422


async def test_checkout_with_same_idempotency_key_returns_same_order(
    test_client: AsyncClient,
    order_session: AsyncSession,
    override_optional_guest: object,
) -> None:
    product = await create_db_product(order_session, stock_quantity=5)
    key = str(uuid4())
    payload = checkout_payload(product)

    first = await test_client.post(
        "/api/v1/orders/checkout",
        json=payload,
        headers={"Idempotency-Key": key},
    )
    second = await test_client.post(
        "/api/v1/orders/checkout",
        json=payload,
        headers={"Idempotency-Key": key},
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert second.json()["id"] == first.json()["id"]


async def test_guest_checkout_works(
    test_client: AsyncClient,
    order_session: AsyncSession,
    override_optional_guest: object,
) -> None:
    product = await create_db_product(order_session)

    response = await test_client.post(
        "/api/v1/orders/checkout",
        json=checkout_payload(product),
        headers={"Idempotency-Key": str(uuid4())},
    )

    assert response.status_code == 201
    assert response.json()["user_id"] is None
    assert response.json()["items"][0]["product_name"] == "Binh gas 12kg"


async def test_guest_lookup_and_cancel(
    test_client: AsyncClient,
    order_session: AsyncSession,
    override_optional_guest: object,
) -> None:
    product = await create_db_product(order_session)
    created = await test_client.post(
        "/api/v1/orders/checkout",
        json=checkout_payload(product),
        headers={"Idempotency-Key": str(uuid4())},
    )
    order = created.json()

    lookup = await test_client.post(
        "/api/v1/orders/lookup",
        json={"order_number": order["order_number"], "phone": "0901234567"},
    )
    cancelled = await test_client.post(
        f"/api/v1/orders/{order['id']}/cancel",
        json={"phone": "0901234567", "reason": "Khach doi lich"},
    )

    assert lookup.status_code == 200
    assert lookup.json()["id"] == order["id"]
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"


async def test_admin_status_update_valid_transition(
    test_client: AsyncClient,
    order_session: AsyncSession,
    override_optional_guest: object,
    override_staff: object,
) -> None:
    product = await create_db_product(order_session)
    created = await test_client.post(
        "/api/v1/orders/checkout",
        json=checkout_payload(product),
        headers={"Idempotency-Key": str(uuid4())},
    )

    response = await test_client.patch(
        f"/api/v1/admin/orders/{created.json()['id']}/status",
        json={"new_status": "confirmed", "notes": "Stock checked"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


async def test_admin_status_update_rejects_invalid_transition(
    test_client: AsyncClient,
    order_session: AsyncSession,
    override_optional_guest: object,
    override_staff: object,
) -> None:
    product = await create_db_product(order_session)
    created = await test_client.post(
        "/api/v1/orders/checkout",
        json=checkout_payload(product),
        headers={"Idempotency-Key": str(uuid4())},
    )

    response = await test_client.patch(
        f"/api/v1/admin/orders/{created.json()['id']}/status",
        json={"new_status": "shipping"},
    )

    assert response.status_code == 400


async def test_admin_list_orders(
    test_client: AsyncClient,
    order_session: AsyncSession,
    override_optional_guest: object,
    override_staff: object,
) -> None:
    product = await create_db_product(order_session)
    await test_client.post(
        "/api/v1/orders/checkout",
        json=checkout_payload(product),
        headers={"Idempotency-Key": str(uuid4())},
    )

    response = await test_client.get("/api/v1/admin/orders")

    assert response.status_code == 200
    assert response.json()["total"] == 1
