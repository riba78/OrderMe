"""
Mock Repositories Module

This module contains mock implementations of repositories for testing
that don't require a database connection.
"""

from typing import List, Dict, Optional, Any, TypeVar, Generic, Callable
from app.models.enums import UserRole, OrderStatus, PaymentStatus, NotificationType

T = TypeVar('T')

class BaseMockRepository(Generic[T]):
    """Base mock repository that stores entities in memory."""
    
    def __init__(self):
        """Initialize an empty storage."""
        self.data: Dict[str, T] = {}
        self.current_id = 1
    
    def get(self, entity_id: str) -> Optional[T]:
        """Get an entity by ID."""
        return self.data.get(str(entity_id))
    
    def get_all(self) -> List[T]:
        """Get all entities."""
        return list(self.data.values())
    
    def add(self, entity: T) -> T:
        """Add an entity."""
        if not hasattr(entity, 'id') or not entity.id:
            entity.id = str(self.current_id)
            self.current_id += 1
        self.data[str(entity.id)] = entity
        return entity
    
    def update(self, entity: T) -> T:
        """Update an entity."""
        if hasattr(entity, 'id') and entity.id in self.data:
            self.data[str(entity.id)] = entity
        return entity
    
    def delete(self, entity_id: str) -> bool:
        """Delete an entity."""
        if str(entity_id) in self.data:
            del self.data[str(entity_id)]
            return True
        return False
    
    def query(self, filter_func: Callable[[T], bool]) -> List[T]:
        """Query entities with a filter function."""
        return [entity for entity in self.data.values() if filter_func(entity)]

class MockUserRepository(BaseMockRepository):
    """Mock user repository for testing."""
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by email."""
        users = self.query(lambda user: user.get('email') == email)
        return users[0] if users else None
    
    def get_by_role(self, role: UserRole) -> List[Dict[str, Any]]:
        """Get users by role."""
        return self.query(lambda user: user.get('role') == role.value)

class MockOrderRepository(BaseMockRepository):
    """Mock order repository for testing."""
    
    def get_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get orders by user ID."""
        return self.query(lambda order: order.get('user_id') == user_id)
    
    def get_by_status(self, status: OrderStatus) -> List[Dict[str, Any]]:
        """Get orders by status."""
        return self.query(lambda order: order.get('status') == status.value)
    
    def update_order_status(self, order_id: str, status: OrderStatus) -> bool:
        """Update order status."""
        order = self.get(order_id)
        if order:
            order['status'] = status.value
            return True
        return False

class MockProductRepository(BaseMockRepository):
    """Mock product repository for testing."""
    
    def get_by_category(self, category_id: str) -> List[Dict[str, Any]]:
        """Get products by category."""
        return self.query(lambda product: product.get('category_id') == category_id)
    
    def get_available(self) -> List[Dict[str, Any]]:
        """Get available products."""
        return self.query(lambda product: product.get('available') == True)
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search products by name or description."""
        query = query.lower()
        return self.query(
            lambda product: 
                query in product.get('name', '').lower() or 
                query in product.get('description', '').lower()
        )

class MockCategoryRepository(BaseMockRepository):
    """Mock category repository for testing."""
    pass

class MockPaymentRepository(BaseMockRepository):
    """Mock payment repository for testing."""
    
    def get_by_order(self, order_id: str) -> List[Dict[str, Any]]:
        """Get payments by order ID."""
        return self.query(lambda payment: payment.get('order_id') == order_id)
    
    def get_by_status(self, status: PaymentStatus) -> List[Dict[str, Any]]:
        """Get payments by status."""
        return self.query(lambda payment: payment.get('status') == status.value)

class MockPaymentMethodRepository(BaseMockRepository):
    """Mock payment method repository for testing."""
    
    def get_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get payment methods by user ID."""
        return self.query(lambda method: method.get('user_id') == user_id)

class MockPaymentInfoRepository(BaseMockRepository):
    """Mock payment info repository for testing."""
    
    def get_by_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Get payment info by payment ID."""
        infos = self.query(lambda info: info.get('payment_id') == payment_id)
        return infos[0] if infos else None 