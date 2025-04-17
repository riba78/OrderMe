"""
Category Controller Module

This module handles all category-related endpoints including:
- Category creation and management
- Category updates
- Category deletion
- Category listing

It provides CRUD operations for product categories and includes
validation to prevent deletion of categories with associated products.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..services.product_service import CategoryService
from ..schemas.product import CategoryCreate, CategoryUpdate, CategoryResponse
from ..dependencies import get_category_service

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
async def get_categories(category_service: CategoryService = Depends(get_category_service)):
    """Get all categories"""
    return category_service.get_categories()

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str, category_service: CategoryService = Depends(get_category_service)):
    """Get a specific category by ID"""
    category = category_service.get_category(category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, category_service: CategoryService = Depends(get_category_service)):
    """Create a new category"""
    try:
        return category_service.create_category(category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    category: CategoryUpdate,
    category_service: CategoryService = Depends(get_category_service)
):
    """Update a category"""
    updated_category = category_service.update_category(category_id, category)
    if updated_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated_category

@router.delete("/{category_id}")
async def delete_category(category_id: str, category_service: CategoryService = Depends(get_category_service)):
    """Delete a category"""
    try:
        success = category_service.delete_category(category_id)
        if not success:
            raise HTTPException(status_code=404, detail="Category not found")
        return {"message": "Category deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 