"""
Product Controller Module

This module handles all product-related endpoints including:
- Product listing and search
- Product creation and updates
- Product availability management
- Product stock management

It provides CRUD operations for products and includes features
like product search, category filtering, availability toggling, and stock updates.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..services.product_service import ProductService
from ..schemas.product import ProductCreate, ProductUpdate, ProductResponse, StockUpdateRequest
from ..dependencies import get_product_service

router = APIRouter()

# Product endpoints
@router.get("/", response_model=List[ProductResponse])
async def get_products(product_service: ProductService = Depends(get_product_service)):
    return product_service.get_products()

@router.get("/available", response_model=List[ProductResponse])
async def get_available_products(product_service: ProductService = Depends(get_product_service)):
    return product_service.get_available_products()

@router.get("/category/{category_id}", response_model=List[ProductResponse])
async def get_products_by_category(category_id: str, product_service: ProductService = Depends(get_product_service)):
    return product_service.get_products_by_category(category_id)

@router.get("/search/{query}", response_model=List[ProductResponse])
async def search_products(query: str, product_service: ProductService = Depends(get_product_service)):
    return product_service.search_products(query)

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, product_service: ProductService = Depends(get_product_service)):
    try:
        return product_service.create_product(product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{product_id}/stock", response_model=ProductResponse)
async def update_product_stock(
    product_id: str, 
    stock_update: StockUpdateRequest,
    product_service: ProductService = Depends(get_product_service)
):
    try:
        updated_product = product_service.update_stock(product_id, stock_update)
        if updated_product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return updated_product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Parameterized routes should come after specific routes
@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, product_service: ProductService = Depends(get_product_service)):
    product = product_service.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}/toggle", response_model=ProductResponse)
async def toggle_product_availability(product_id: str, product_service: ProductService = Depends(get_product_service)):
    updated_product = product_service.toggle_product_availability(product_id)
    if updated_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product: ProductUpdate,
    product_service: ProductService = Depends(get_product_service)
):
    try:
        updated_product = product_service.update_product(product_id, product)
        if updated_product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return updated_product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 