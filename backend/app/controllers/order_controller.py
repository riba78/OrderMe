"""
Order Controller Module

This module handles all order-related endpoints including:
- Order creation and management
- Order status updates
- Order history retrieval
- Order listing and filtering

It provides CRUD operations for orders and includes order-specific
functionality like status updates and history tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from app.models.order import Order, OrderItem
from app.models import OrderStatus
from app.models.product import Product
from app.services.order_service import OrderService
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse
from app.database import get_db
from app.dependencies import get_order_service

router = APIRouter()

# Endpoints
@router.get("/test")
async def test_order():
    """Test endpoint to verify the order controller is working"""
    return {"message": "Order controller is working"}

@router.get("/", response_model=List[OrderResponse])
def get_orders(
    user_id: Optional[UUID] = None,
    status: Optional[OrderStatus] = None,
    order_service: OrderService = Depends(get_order_service)
):
    if user_id:
        return order_service.get_orders_by_user(user_id)
    elif status:
        return order_service.get_orders_by_status(status)
    else:
        return order_service.get_orders()

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: UUID,
    order_service: OrderService = Depends(get_order_service)
):
    order = order_service.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order: OrderCreate,
    order_service: OrderService = Depends(get_order_service)
):
    try:
        return order_service.create_order(order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: UUID,
    order: OrderUpdate,
    order_service: OrderService = Depends(get_order_service)
):
    updated_order = order_service.update_order(order_id, order)
    if updated_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated_order

@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: UUID,
    status: OrderStatus,
    order_service: OrderService = Depends(get_order_service)
):
    try:
        updated_order = order_service.update_order_status(order_id, status)
        if updated_order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return updated_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: UUID,
    order_service: OrderService = Depends(get_order_service)
):
    try:
        cancelled_order = order_service.cancel_order(order_id)
        if cancelled_order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return cancelled_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{user_id}", response_model=List[OrderResponse])
def get_user_orders(
    user_id: UUID,
    order_service: OrderService = Depends(get_order_service)
):
    return order_service.get_orders_by_user(user_id)

@router.get("/status/{status}", response_model=List[OrderResponse])
def get_orders_by_status(
    status: OrderStatus,
    order_service: OrderService = Depends(get_order_service)
):
    return order_service.get_orders_by_status(status) 