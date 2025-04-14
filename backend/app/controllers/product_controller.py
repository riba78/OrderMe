"""
Product Controller Module

This module handles all product-related endpoints including:
- Product listing and search
- Product creation and updates
- Product availability management
- Product category management

It provides CRUD operations for products and includes features
like product search, category filtering, and availability toggling.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..services.product_service import ProductService, CategoryService
from ..schemas.product import ProductCreate, ProductUpdate, ProductResponse, CategoryCreate, CategoryUpdate, CategoryResponse
from ..dependencies import get_product_service, get_category_service

router = APIRouter()

# Product endpoints
@router.get("/products/", response_model=List[ProductResponse])
def get_products(product_service: ProductService = Depends(get_product_service)):
    return product_service.get_products()

@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, product_service: ProductService = Depends(get_product_service)):
    product = product_service.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/products/category/{category_id}", response_model=List[ProductResponse])
def get_products_by_category(category_id: str, product_service: ProductService = Depends(get_product_service)):
    return product_service.get_products_by_category(category_id)

@router.get("/products/available", response_model=List[ProductResponse])
def get_available_products(product_service: ProductService = Depends(get_product_service)):
    return product_service.get_available_products()

@router.get("/products/search/{query}", response_model=List[ProductResponse])
def search_products(query: str, product_service: ProductService = Depends(get_product_service)):
    return product_service.search_products(query)

@router.post("/products/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, product_service: ProductService = Depends(get_product_service)):
    try:
        return product_service.create_product(product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    product: ProductUpdate,
    product_service: ProductService = Depends(get_product_service)
):
    updated_product = product_service.update_product(product_id, product)
    if updated_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.put("/products/{product_id}/toggle", response_model=ProductResponse)
def toggle_product_availability(product_id: str, product_service: ProductService = Depends(get_product_service)):
    updated_product = product_service.toggle_product_availability(product_id)
    if updated_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

# Category endpoints
@router.get("/categories/", response_model=List[CategoryResponse])
def get_categories(category_service: CategoryService = Depends(get_category_service)):
    return category_service.get_categories()

@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: str, category_service: CategoryService = Depends(get_category_service)):
    category = category_service.get_category(category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/categories/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, category_service: CategoryService = Depends(get_category_service)):
    return category_service.create_category(category)

@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: str,
    category: CategoryUpdate,
    category_service: CategoryService = Depends(get_category_service)
):
    updated_category = category_service.update_category(category_id, category)
    if updated_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated_category

@router.delete("/categories/{category_id}")
def delete_category(category_id: str, category_service: CategoryService = Depends(get_category_service)):
    try:
        success = category_service.delete_category(category_id)
        if not success:
            raise HTTPException(status_code=404, detail="Category not found")
        return {"message": "Category deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 