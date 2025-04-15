"""
User Model Tests

This module contains unit tests for the User-related models:
- User
- AdminManager
- Customer
- UserProfile

Tests cover:
- Model validation
- Relationships
- Role enumeration
- Default values
- Business logic constraints
"""

import pytest
from uuid import uuid4
from datetime import datetime
from app.models import User, AdminManager, Customer, UserProfile, UserRole
from app.schemas.user import UserCreate, AdminManagerCreate, CustomerCreate, UserProfileCreate

def test_create_user(test_db):
    """Test creating a new user."""
    user_id = str(uuid4())
    user = User(
        id=user_id,
        role=UserRole.CUSTOMER.value,
        email="test@example.com"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    assert user.id == user_id
    assert user.role.value == UserRole.CUSTOMER.value
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)

def test_create_admin_manager(test_db):
    """Test creating a new admin/manager."""
    user = User(
        id=str(uuid4()),
        role=UserRole.ADMIN.value,
        email="admin@example.com"
    )
    test_db.add(user)
    test_db.commit()

    admin = AdminManager(
        user_id=user.id,
        email="admin@test.com",
        hashed_password="hashed_password",
        verification_method="email",
        tin_trunk_number="12345"
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)

    assert admin.user_id == user.id
    assert admin.email == "admin@test.com"
    assert admin.verification_method == "email"
    assert admin.user.role.value == UserRole.ADMIN.value

def test_create_customer(test_db):
    """Test creating a new customer."""
    # Create manager user first
    manager = User(
        id=str(uuid4()),
        role=UserRole.MANAGER.value,
        email="manager@example.com"
    )
    test_db.add(manager)
    test_db.commit()

    # Create manager profile
    admin_manager = AdminManager(
        user_id=manager.id,
        email="manager@test.com",
        hashed_password="hashed_password",
        verification_method="email"
    )
    test_db.add(admin_manager)
    test_db.commit()

    # Create customer user
    user = User(
        id=str(uuid4()),
        role=UserRole.CUSTOMER.value,
        email="customer@example.com"
    )
    test_db.add(user)
    test_db.commit()

    customer = Customer(
        user_id=user.id,
        phone_number="+1234567890",
        created_by=manager.id,
        assigned_manager_id=manager.id
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)

    assert customer.user_id == user.id
    assert customer.phone_number == "+1234567890"
    assert customer.created_by == manager.id
    assert customer.assigned_manager_id == manager.id
    assert customer.user.role.value == UserRole.CUSTOMER.value

def test_create_user_profile(test_db):
    """Test creating a new user profile."""
    user = User(
        id=str(uuid4()),
        role=UserRole.CUSTOMER.value,
        email="profile@example.com"
    )
    test_db.add(user)
    test_db.commit()

    profile = UserProfile(
        user_id=user.id,
        first_name="John",
        last_name="Doe",
        business_name="Test Business"
    )
    test_db.add(profile)
    test_db.commit()
    test_db.refresh(profile)

    assert profile.user_id == user.id
    assert profile.first_name == "John"
    assert profile.last_name == "Doe"
    assert profile.business_name == "Test Business"

def test_user_relationships(test_db):
    """Test relationships between User and related models."""
    # Create manager
    manager_user = User(
        id=str(uuid4()), 
        role=UserRole.MANAGER.value,
        email="relationship_manager@example.com"
    )
    test_db.add(manager_user)
    test_db.commit()

    manager = AdminManager(
        user_id=manager_user.id,
        email="manager@test.com",
        hashed_password="hashed_password",
        verification_method="email"
    )
    test_db.add(manager)
    test_db.commit()

    # Create customer
    customer_user = User(
        id=str(uuid4()), 
        role=UserRole.CUSTOMER.value,
        email="relationship_customer@example.com"
    )
    test_db.add(customer_user)
    test_db.commit()

    customer = Customer(
        user_id=customer_user.id,
        phone_number="+1234567890",
        created_by=manager_user.id,
        assigned_manager_id=manager_user.id
    )
    test_db.add(customer)

    profile = UserProfile(
        user_id=customer_user.id,
        first_name="John",
        last_name="Doe"
    )
    test_db.add(profile)
    test_db.commit()

    # Test relationships
    assert customer_user.customer.phone_number == "+1234567890"
    assert customer_user.profile.first_name == "John"
    assert customer.assigned_manager_id == manager_user.id

def test_user_validation():
    """Test UserCreate schema validation."""
    valid_data = {
        "role": UserRole.CUSTOMER,
        "email": "test@example.com",
        "password": "securepass123"
    }
    user = UserCreate(**valid_data)
    assert user.role == UserRole.CUSTOMER
    assert user.email == "test@example.com"

    # Test invalid email
    with pytest.raises(ValueError):
        UserCreate(**{**valid_data, "email": "invalid-email"})

    # Test invalid password (too short)
    with pytest.raises(ValueError):
        UserCreate(**{**valid_data, "password": "short"})

def test_admin_manager_validation():
    """Test AdminManagerCreate schema validation."""
    valid_data = {
        "user_id": str(uuid4()),
        "email": "admin@test.com",
        "password": "securepassword",  # Will be hashed
        "verification_method": "email",
        "tin_trunk_number": "12345"
    }
    admin = AdminManagerCreate(**valid_data)
    assert admin.email == valid_data["email"]

    # Test invalid email
    with pytest.raises(ValueError):
        AdminManagerCreate(**{**valid_data, "email": "invalid-email"}) 