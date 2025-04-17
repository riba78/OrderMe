"""
Payment Controller Module

This module handles all payment-related endpoints including:
- Payment processing
- Payment status updates
- Payment method management
- Payment information management
- Refund processing

It provides CRUD operations for payments and includes payment-specific
functionality like processing and refunds.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from app.models.payment import Payment, PaymentStatus, PaymentMethod, PaymentInfo
from app.models.order import Order
from app.services.payment_service import PaymentService, PaymentMethodService, PaymentInfoService
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentResponse, PaymentMethodCreate, PaymentMethodUpdate, PaymentMethodResponse, PaymentInfoCreate, PaymentInfoUpdate, PaymentInfoResponse
from app.database import get_db
from app.dependencies import get_payment_service, get_payment_method_service, get_payment_info_service

router = APIRouter()

# Endpoints
@router.get("/test")
async def test_payment():
    """Test endpoint to verify the payment controller is working"""
    return {"message": "Payment controller is working"}

@router.get("/payments/", response_model=List[PaymentResponse])
def get_payments(payment_service: PaymentService = Depends(get_payment_service)):
    return payment_service.get_payments()

@router.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, payment_service: PaymentService = Depends(get_payment_service)):
    payment = payment_service.get_payment(payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.get("/payments/order/{order_id}", response_model=PaymentResponse)
def get_payment_by_order(order_id: int, payment_service: PaymentService = Depends(get_payment_service)):
    payment = payment_service.get_payment_by_order(order_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.get("/payments/status/{status}", response_model=List[PaymentResponse])
def get_payments_by_status(status: PaymentStatus, payment_service: PaymentService = Depends(get_payment_service)):
    return payment_service.get_payments_by_status(status)

@router.get("/payments/pending", response_model=List[PaymentResponse])
def get_pending_payments(payment_service: PaymentService = Depends(get_payment_service)):
    return payment_service.get_pending_payments()

@router.post("/payments/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment: PaymentCreate, payment_service: PaymentService = Depends(get_payment_service)):
    try:
        return payment_service.create_payment(payment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/payments/{payment_id}/status", response_model=PaymentResponse)
def update_payment_status(
    payment_id: int,
    status: PaymentStatus,
    payment_service: PaymentService = Depends(get_payment_service)
):
    updated_payment = payment_service.update_payment_status(payment_id, status)
    if updated_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return updated_payment

@router.put("/payments/{payment_id}/process", response_model=PaymentResponse)
def process_payment(payment_id: int, payment_service: PaymentService = Depends(get_payment_service)):
    updated_payment = payment_service.process_payment(payment_id)
    if updated_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found or not in pending status")
    return updated_payment

@router.put("/payments/{payment_id}/refund", response_model=PaymentResponse)
def refund_payment(payment_id: int, payment_service: PaymentService = Depends(get_payment_service)):
    updated_payment = payment_service.refund_payment(payment_id)
    if updated_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found or not in completed status")
    return updated_payment

# Payment Method endpoints
@router.get("/payment-methods/", response_model=List[PaymentMethodResponse])
def get_payment_methods(payment_service: PaymentService = Depends(get_payment_service)):
    return payment_service.get_payment_methods()

@router.get("/payment-methods/{payment_method_id}", response_model=PaymentMethodResponse)
def get_payment_method(payment_method_id: str, payment_service: PaymentService = Depends(get_payment_service)):
    payment_method = payment_service.get_payment_method(payment_method_id)
    if payment_method is None:
        raise HTTPException(status_code=404, detail="Payment method not found")
    return payment_method

@router.get("/payment-methods/user/{user_id}", response_model=List[PaymentMethodResponse])
def get_user_payment_methods(user_id: str, payment_service: PaymentService = Depends(get_payment_service)):
    return payment_service.get_user_payment_methods(user_id)

@router.post("/payment-methods/", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
def create_payment_method(
    payment_method: PaymentMethodCreate,
    payment_service: PaymentService = Depends(get_payment_service)
):
    try:
        return payment_service.create_payment_method(payment_method)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/payment-methods/{payment_method_id}", response_model=PaymentMethodResponse)
def update_payment_method(
    payment_method_id: str,
    payment_method: PaymentMethodUpdate,
    payment_service: PaymentService = Depends(get_payment_service)
):
    updated_payment_method = payment_service.update_payment_method(payment_method_id, payment_method)
    if updated_payment_method is None:
        raise HTTPException(status_code=404, detail="Payment method not found")
    return updated_payment_method

@router.delete("/payment-methods/{payment_method_id}")
def delete_payment_method(payment_method_id: str, payment_service: PaymentService = Depends(get_payment_service)):
    try:
        success = payment_service.delete_payment_method(payment_method_id)
        if not success:
            raise HTTPException(status_code=404, detail="Payment method not found")
        return {"message": "Payment method deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Payment Info endpoints
@router.get("/payment-info/", response_model=List[PaymentInfoResponse])
def get_payment_infos(payment_service: PaymentService = Depends(get_payment_service)):
    return payment_service.get_payment_infos()

@router.get("/payment-info/{payment_info_id}", response_model=PaymentInfoResponse)
def get_payment_info(payment_info_id: str, payment_service: PaymentService = Depends(get_payment_service)):
    payment_info = payment_service.get_payment_info(payment_info_id)
    if payment_info is None:
        raise HTTPException(status_code=404, detail="Payment info not found")
    return payment_info

@router.get("/payment-info/user/{user_id}", response_model=List[PaymentInfoResponse])
def get_user_payment_infos(user_id: str, payment_service: PaymentService = Depends(get_payment_service)):
    return payment_service.get_user_payment_infos(user_id)

@router.post("/payment-info/", response_model=PaymentInfoResponse, status_code=status.HTTP_201_CREATED)
def create_payment_info(
    payment_info: PaymentInfoCreate,
    payment_service: PaymentService = Depends(get_payment_service)
):
    try:
        return payment_service.create_payment_info(payment_info)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/payment-info/{payment_info_id}", response_model=PaymentInfoResponse)
def update_payment_info(
    payment_info_id: str,
    payment_info: PaymentInfoCreate,
    payment_service: PaymentService = Depends(get_payment_service)
):
    updated_payment_info = payment_service.update_payment_info(payment_info_id, payment_info)
    if updated_payment_info is None:
        raise HTTPException(status_code=404, detail="Payment info not found")
    return updated_payment_info

@router.delete("/payment-info/{payment_info_id}")
def delete_payment_info(payment_info_id: str, payment_service: PaymentService = Depends(get_payment_service)):
    try:
        success = payment_service.delete_payment_info(payment_info_id)
        if not success:
            raise HTTPException(status_code=404, detail="Payment info not found")
        return {"message": "Payment info deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 