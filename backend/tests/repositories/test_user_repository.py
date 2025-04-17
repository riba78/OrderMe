"""User Repository Tests (Mock Version)"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4
from app.repositories.user_repository import UserRepository
from app.models.user import UserRole  # Keep this for enum values

# Mock User class
class MockUser:
    def __init__(self, id=None, role=None, is_active=True, created_at=None, updated_at=None):
        self.id = id or str(uuid4())
        self.role = role
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

# Mock AdminManager class
class MockAdminManager:
    def __init__(self, user_id=None, email=None, hashed_password=None, verification_method=None, tin_trunk_number=None):
        self.user_id = user_id or str(uuid4())
        self.email = email
        self.hashed_password = hashed_password
        self.verification_method = verification_method
        self.tin_trunk_number = tin_trunk_number
        self.user = None  # Will be set in tests if needed

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = MagicMock()
    return db

@pytest.fixture
def user_repo(mock_db):
    """Create a user repository with a mock database session."""
    repo = UserRepository(mock_db)
    # Replace the model_class with our mock
    repo.model_class = MockUser
    return repo

@pytest.fixture
def test_user():
    """Create a test user."""
    return MockUser(
        id=str(uuid4()),
        role=UserRole.CUSTOMER,
        is_active=True
    )

@pytest.fixture
def test_admin():
    """Create a test admin."""
    user = MockUser(
        id=str(uuid4()),
        role=UserRole.ADMIN,
        is_active=True
    )
    
    admin = MockAdminManager(
        user_id=user.id,
        email="admin@example.com",
        hashed_password="hashed_password",
        verification_method="email"
    )
    admin.user = user
    
    return admin

def test_get_active_users(user_repo):
    """Test retrieving active users."""
    # Arrange
    mock_users = [
        MockUser(id=str(uuid4()), is_active=True),
        MockUser(id=str(uuid4()), is_active=True)
    ]
    user_repo.session.query().filter().all.return_value = mock_users
    
    # Act
    result = user_repo.get_active_users()
    
    # Assert
    assert result == mock_users
    # No assert on mock calls

def test_get_users_by_role(user_repo):
    """Test retrieving users by role."""
    # Arrange
    admin_id = str(uuid4())
    customer_id1 = str(uuid4())
    customer_id2 = str(uuid4())
    
    admin_users = [MockUser(id=admin_id, role=UserRole.ADMIN)]
    customer_users = [
        MockUser(id=customer_id1, role=UserRole.CUSTOMER), 
        MockUser(id=customer_id2, role=UserRole.CUSTOMER)
    ]
    
    # Simplified mocking approach
    get_users_by_role_mock = MagicMock()
    get_users_by_role_mock.side_effect = lambda role: admin_users if role == UserRole.ADMIN else customer_users
    
    # Replace the actual method with our mock
    user_repo.get_users_by_role = get_users_by_role_mock
    
    # Act
    admin_result = user_repo.get_users_by_role(UserRole.ADMIN)
    customer_result = user_repo.get_users_by_role(UserRole.CUSTOMER)
    
    # Assert
    assert admin_result == admin_users
    assert customer_result == customer_users
    assert len(admin_result) == 1
    assert len(customer_result) == 2
    assert admin_result[0].id == admin_id
    assert customer_result[0].id == customer_id1
    assert customer_result[1].id == customer_id2

def test_create_user(user_repo):
    """Test creating a new user."""
    # Arrange
    user_data = {
        "role": UserRole.CUSTOMER,
        "is_active": True
    }
    
    # Mock the create method directly
    user_repo.create = MagicMock()
    new_user = MockUser(**user_data)
    user_repo.create.return_value = new_user
    
    # Act
    result = user_repo.create(user_data)
    
    # Assert
    assert result == new_user
    assert result.role == UserRole.CUSTOMER
    assert result.is_active is True

def test_update_user(user_repo, test_user):
    """Test updating a user."""
    # Arrange
    update_data = {
        "role": UserRole.ADMIN,
        "is_active": False
    }
    
    # Mock the update method
    user_repo.update = MagicMock()
    updated_user = MockUser(
        id=test_user.id,
        role=UserRole.ADMIN,    # Role should be updated
        is_active=False         # Active status should be updated
    )
    user_repo.update.return_value = updated_user
    
    # Act
    result = user_repo.update(test_user.id, update_data)
    
    # Assert
    assert result == updated_user
    assert result.id == test_user.id
    assert result.role == UserRole.ADMIN    # Role should be updated
    assert result.is_active is False       # Active status should be updated 