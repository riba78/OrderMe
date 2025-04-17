"""
Product Controller Tests

These tests verify that all product-related endpoints work correctly.
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.models.enums import UserRole

# Mock category data
mock_category = {
    "id": "1",
    "name": "Test Category",
    "description": "This is a test category"
}

# Mock product data
mock_product = {
    "id": "1",
    "product_name": "Test Product",
    "description": "This is a test product",
    "price": 19.99,
    "image_url": "http://example.com/image.jpg",
    "category_id": "1",
    "is_available": True,
    "min_stock_level": 5,
    "max_stock_level": 100,
    "qty_in_stock": 50,
    "created_by": "1",
    "category": mock_category,
    "is_in_stock": True,
    "needs_restock": False
}

def setup_mock_product_service(mock_service):
    """Configure the mock product service with test data."""
    mock_service.get_products.return_value = [mock_product]
    mock_service.get_product.return_value = mock_product
    mock_service.create_product.return_value = mock_product
    mock_service.update_product.return_value = mock_product
    mock_service.get_products_by_category.return_value = [mock_product]
    mock_service.get_available_products.return_value = [mock_product]
    mock_service.search_products.return_value = [mock_product]
    mock_service.toggle_product_availability.return_value = mock_product
    mock_service.update_stock.return_value = mock_product
    return mock_service

def setup_mock_category_service(mock_service):
    """Configure the mock category service with test data."""
    mock_service.get_categories.return_value = [mock_category]
    mock_service.get_category.return_value = mock_category
    mock_service.create_category.return_value = mock_category
    mock_service.update_category.return_value = mock_category
    mock_service.delete_category.return_value = True
    return mock_service

def test_get_products(test_client, mock_product_service):
    """Test getting all products."""
    setup_mock_product_service(mock_product_service)
    response = test_client.get("/products/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["product_name"] == mock_product["product_name"]
    assert mock_product_service.get_products.called

def test_get_product_by_id(test_client, mock_product_service):
    """Test getting a product by ID."""
    setup_mock_product_service(mock_product_service)
    response = test_client.get("/products/1")
    assert response.status_code == 200
    assert response.json()["product_name"] == mock_product["product_name"]
    mock_product_service.get_product.assert_called_with("1")
    
    # Test non-existent product
    mock_product_service.get_product.return_value = None
    response = test_client.get("/products/999")
    assert response.status_code == 404

def test_get_products_by_category(test_client, mock_product_service):
    """Test getting products by category."""
    setup_mock_product_service(mock_product_service)
    response = test_client.get("/products/category/1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["product_name"] == mock_product["product_name"]
    mock_product_service.get_products_by_category.assert_called_with("1")

def test_get_available_products(test_client, mock_product_service):
    """Test getting available products."""
    setup_mock_product_service(mock_product_service)
    response = test_client.get("/products/available")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["product_name"] == mock_product["product_name"]
    assert mock_product_service.get_available_products.called

def test_search_products(test_client, mock_product_service):
    """Test searching for products."""
    setup_mock_product_service(mock_product_service)
    response = test_client.get("/products/search/test")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["product_name"] == mock_product["product_name"]
    mock_product_service.search_products.assert_called_with("test")

def test_create_product(test_client, mock_product_service):
    """Test creating a product."""
    setup_mock_product_service(mock_product_service)
    product_data = {
        "product_name": "New Product",
        "description": "This is a new product",
        "price": 19.99,
        "image_url": "http://example.com/new-image.jpg",
        "category_id": "1",
        "is_available": True,
        "min_stock_level": 5,
        "max_stock_level": 100,
        "qty_in_stock": 50,
        "created_by": "1"
    }
    response = test_client.post("/products/", json=product_data)
    assert response.status_code == 201
    assert response.json()["product_name"] == mock_product["product_name"]
    mock_product_service.create_product.assert_called_once()
    
    # Test creating product with validation error
    mock_product_service.create_product.side_effect = ValueError("Invalid product data")
    response = test_client.post("/products/", json=product_data)
    assert response.status_code == 400
    assert "Invalid product data" in response.json()["detail"]

def test_update_product(test_client, mock_product_service):
    """Test updating a product."""
    setup_mock_product_service(mock_product_service)
    update_data = {
        "product_name": "Updated Product",
        "price": 15.99
    }
    response = test_client.put("/products/1", json=update_data)
    assert response.status_code == 200
    assert response.json()["product_name"] == mock_product["product_name"]

    # Test updating non-existent product
    mock_product_service.update_product.return_value = None
    response = test_client.put("/products/999", json=update_data)
    assert response.status_code == 404

def test_toggle_product_availability(test_client, mock_product_service):
    """Test toggling product availability."""
    setup_mock_product_service(mock_product_service)
    response = test_client.put("/products/1/toggle")
    assert response.status_code == 200
    assert response.json()["product_name"] == mock_product["product_name"]
    mock_product_service.toggle_product_availability.assert_called_with("1")
    
    # Test toggling non-existent product
    mock_product_service.toggle_product_availability.return_value = None
    response = test_client.put("/products/999/toggle")
    assert response.status_code == 404

def test_get_categories(test_client, mock_category_service):
    """Test getting all categories."""
    setup_mock_category_service(mock_category_service)
    response = test_client.get("/categories/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == mock_category["name"]
    assert mock_category_service.get_categories.called

def test_get_category_by_id(test_client, mock_category_service):
    """Test getting a category by ID."""
    setup_mock_category_service(mock_category_service)
    response = test_client.get("/categories/1")
    assert response.status_code == 200
    assert response.json()["name"] == mock_category["name"]
    mock_category_service.get_category.assert_called_with("1")
    
    # Test non-existent category
    mock_category_service.get_category.return_value = None
    response = test_client.get("/categories/999")
    assert response.status_code == 404

def test_create_category(test_client, mock_category_service):
    """Test creating a category."""
    setup_mock_category_service(mock_category_service)
    category_data = {
        "name": "New Category",
        "description": "This is a new category"
    }
    response = test_client.post("/categories/", json=category_data)
    assert response.status_code == 201
    assert response.json()["name"] == mock_category["name"]
    mock_category_service.create_category.assert_called_once()

    # Test creating category with validation error
    mock_category_service.create_category.side_effect = ValueError("Invalid category data")
    response = test_client.post("/categories/", json=category_data)
    assert response.status_code == 400
    assert "Invalid category data" in response.json()["detail"]

def test_update_category(test_client, mock_category_service):
    """Test updating a category."""
    setup_mock_category_service(mock_category_service)
    update_data = {
        "name": "Updated Category",
        "description": "This is an updated category"
    }
    response = test_client.put("/categories/1", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == mock_category["name"]
    mock_category_service.update_category.assert_called_with("1", update_data)
    
    # Test updating non-existent category
    mock_category_service.update_category.return_value = None
    response = test_client.put("/categories/999", json=update_data)
    assert response.status_code == 404

def test_delete_category(test_client, mock_category_service):
    """Test deleting a category."""
    setup_mock_category_service(mock_category_service)
    response = test_client.delete("/categories/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Category deleted successfully"}
    mock_category_service.delete_category.assert_called_with("1")
    
    # Test deleting non-existent category
    mock_category_service.delete_category.return_value = False
    response = test_client.delete("/categories/999")
    assert response.status_code == 404
    
    # Test deleting with error
    mock_category_service.delete_category.side_effect = ValueError("Cannot delete category with products")
    response = test_client.delete("/categories/1")
    assert response.status_code == 400
    assert "Cannot delete category with products" in response.json()["detail"] 