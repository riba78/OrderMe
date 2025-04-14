"""
Order Controller Module

This module handles all order-related endpoints including:
- Order creation and management
- Order status updates
- Order history and tracking
- Order cancellation

It provides CRUD operations for orders and includes business logic
for order processing, status management, and validation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, conlist
from app.models.models import Order, OrderItem, OrderStatus, Product
from app.database import get_db
from app.controllers.auth_controller import get_current_user
from ..services.order_service import OrderService
from ..schemas.order import OrderCreate, OrderUpdate, OrderResponse
from ..dependencies import get_order_service
from ..models.models import OrderStatus

router = APIRouter()

# Pydantic models
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: conlist(OrderItemCreate, min_items=1)

class OrderItemResponse(OrderItemCreate):
    id: int
    unit_price: float

    class Config:
        orm_mode = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: float
    items: List[OrderItemResponse]

    class Config:
        orm_mode = True

# Endpoints
@router.get("/test")
async def test_order():
    """Test endpoint to verify the order controller is working"""
    return {"message": "Order controller is working"}

@router.get("/orders/", response_model=List[OrderResponse])
def get_orders(order_service: OrderService = Depends(get_order_service)):
    return order_service.get_orders()

@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, order_service: OrderService = Depends(get_order_service)):
    order = order_service.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/orders/user/{user_id}", response_model=List[OrderResponse])
def get_user_orders(user_id: str, order_service: OrderService = Depends(get_order_service)):
    return order_service.get_user_orders(user_id)

@router.get("/orders/status/{status}", response_model=List[OrderResponse])
def get_orders_by_status(status: OrderStatus, order_service: OrderService = Depends(get_order_service)):
    return order_service.get_orders_by_status(status)

@router.post("/orders/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate, order_service: OrderService = Depends(get_order_service)):
    try:
        return order_service.create_order(order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/orders/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: str,
    order: OrderUpdate,
    order_service: OrderService = Depends(get_order_service)
):
    updated_order = order_service.update_order(order_id, order)
    if updated_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated_order

@router.put("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: str,
    status: OrderStatus,
    order_service: OrderService = Depends(get_order_service)
):
    updated_order = order_service.update_order_status(order_id, status)
    if updated_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated_order

@router.put("/orders/{order_id}/tracking", response_model=OrderResponse)
def update_tracking_number(
    order_id: str,
    tracking_number: str,
    order_service: OrderService = Depends(get_order_service)
):
    updated_order = order_service.update_tracking_number(order_id, tracking_number)
    if updated_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated_order 