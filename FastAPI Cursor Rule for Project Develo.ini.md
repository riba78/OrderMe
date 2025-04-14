# FastAPI Cursor Rule for Project Development

This document provides a set of guidelines (a "cursor rule") to help you develop your full stack application backend using FastAPI. It outlines best practices, project structure recommendations, and specific instructions on how to write code that adheres to SOLID principles.

---

## 1. Overview

- **Framework:** FastAPI
- **Language:** Python
- **Architecture:** Layered approach following SOLID principles
  - **Models/ORM:** Data classes representing your database schema (using SQLAlchemy/Pydantic)
  - **Schemas:** Pydantic models for request/response validation
  - **Services:** Business logic and workflows
  - **Repositories:** Data access layer (CRUD operations)
  - **Controllers/Endpoints:** API endpoints using FastAPI's routing (APIRouter)
- **Goal:** Create a maintainable, scalable, and robust backend that cleanly integrates with the frontend (Vue).

---

## 2. Project Structure

```plaintext
backend/
│
├── app/
│   ├── __init__.py
│   ├── config.py              # Environment-specific configuration
│   ├── database.py            # Database connection and session management
│   ├── main.py               # Application entry point
│   │
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base.py           # Base model with common fields
│   │   ├── user.py           # User, AdminManager, Customer models
│   │   ├── product.py        # Product and Category models
│   │   ├── order.py          # Order and OrderItem models
│   │   ├── payment.py        # Payment, PaymentMethod, PaymentInfo models
│   │   └── notification.py   # Notification model
│   │
│   ├── schemas/              # Pydantic models for API
│   │   ├── __init__.py
│   │   ├── user.py          # User-related schemas
│   │   ├── product.py       # Product and category schemas
│   │   ├── order.py         # Order schemas
│   │   └── payment.py       # Payment schemas
│   │
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   ├── base_service.py  # Base service with common operations
│   │   ├── user_service.py  # Authentication and user management
│   │   ├── product_service.py # Product and category management
│   │   ├── order_service.py  # Order processing
│   │   └── payment_service.py # Payment processing
│   │
│   ├── repositories/        # Data access layer
│   │   ├── __init__.py
│   │   ├── base_repository.py # Generic repository with CRUD
│   │   ├── user_repository.py # User data access
│   │   ├── product_repository.py # Product data access
│   │   ├── order_repository.py  # Order data access
│   │   └── payment_repository.py # Payment data access
│   │
│   └── controllers/         # API endpoints
│       ├── __init__.py
│       ├── auth_controller.py    # Authentication
│       ├── user_controller.py    # User management
│       ├── product_controller.py # Product operations
│       ├── order_controller.py   # Order operations
│       └── payment_controller.py # Payment processing
│
├── requirements.txt         # Python dependencies
└── .gitignore              # Git ignore patterns

---

## 3. Implementation Guidelines

### 3.1 Database Connection
- Use `database.py` for connection management:
  ```python
  from sqlalchemy import create_engine
  from sqlalchemy.orm import sessionmaker, Session
  from sqlalchemy.pool import QueuePool
  from contextlib import contextmanager
  from typing import Generator

  @contextmanager
  def get_db() -> Generator[Session, None, None]:
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()
  ```

### 3.2 Configuration Management
- Use `config.py` for environment-specific settings
- Never commit sensitive data
- Use environment variables with sensible defaults:
  ```python
  DATABASE_CONFIG = {
      "host": os.getenv("DB_HOST", "default_host"),
      "port": os.getenv("DB_PORT", "3306"),
      # ... other config
  }
  ```

### 3.3 Model Structure
- Base model with common fields:
  ```python
  class Base:
      id: str  # UUID
      created_at: datetime
      updated_at: datetime
  ```
- Separate SQLAlchemy models and Pydantic schemas
- Use type hints and field validation

### 3.4 Repository Pattern
- Extend BaseRepository for CRUD operations:
  ```python
  class BaseRepository:
      def get(self, id: int) -> Optional[Any]
      def get_all(self) -> List[Any]
      def create(self, obj: Any) -> Any
      def update(self, obj: Any) -> Any
      def delete(self, id: int) -> bool
  ```

### 3.5 Service Layer
- Implement business logic
- Handle transactions
- Coordinate between repositories
- Validate business rules

### 3.6 Controller Design
- Use FastAPI dependency injection
- Define clear request/response models
- Group related endpoints using APIRouter
- Implement proper error handling

---

## 4. Best Practices

### 4.1 Error Handling
- Use custom exceptions for business logic
- Implement proper HTTP status codes
- Provide meaningful error messages

### 4.2 Security
- Store sensitive data in environment variables
- Use proper password hashing
- Implement JWT authentication
- Validate input data

### 4.3 Performance
- Use connection pooling
- Implement proper indexing
- Cache when necessary
- Use async operations where appropriate

### 4.4 Testing
- Write unit tests for services
- Test API endpoints
- Mock database operations
- Use pytest for testing

---

## 5. Development Workflow

1. Define models and schemas
2. Implement repositories
3. Create services with business logic
4. Build API endpoints
5. Test and document
6. Review and refactor

---

## 6. Deployment Considerations

- Use environment variables
- Implement proper logging
- Set up monitoring
- Configure CORS
- Use HTTPS in production
- Implement rate limiting