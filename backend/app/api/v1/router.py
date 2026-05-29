"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, orders, products

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(products.router, tags=["Products"])
api_router.include_router(orders.router, tags=["Orders"])
