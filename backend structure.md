this is current backend structure that will be extended with other classes during the development

backend/
│
├── app/
│   ├── __init__.py
│   ├── config.py            # Configuration settings (database URL, JWT secret)
│   ├── main.py              # Application entry point
│   ├── database.py          # Database connection and session management
│   │
│   ├── models/              # Data classes and ORM models
│   │   ├── __init__.py
│   │   ├── base.py          # Base model with common fields (timestamps)
│   │   ├── user.py          # User, AdminManager, Customer models
│   │   ├── product.py       # Product and Category models
│   │   ├── order.py         # Order and OrderItem models
│   │   ├── payment.py       # Payment, PaymentMethod, PaymentInfo models
│   │   └── notification.py  # Notification model
│   │
│   ├── schemas/             # Pydantic schemas for request/response validation
│   │   ├── __init__.py
│   │   ├── user.py          # User-related schemas
│   │   ├── product.py       # Product and Category schemas
│   │   ├── order.py         # Order schemas
│   │   └── payment.py       # Payment schemas
│   │
│   ├── services/            # Business logic and workflows
│   │   ├── __init__.py
│   │   ├── base_service.py  # Base service with common operations
│   │   ├── user_service.py  # User authentication and profile management
│   │   ├── product_service.py # Product and category management
│   │   ├── order_service.py  # Order processing and management
│   │   └── payment_service.py # Payment processing and management
│   │
│   ├── repositories/        # Data access and persistence logic
│   │   ├── __init__.py
│   │   ├── base_repository.py # Generic repository with common CRUD operations
│   │   ├── user_repository.py # User data access
│   │   ├── product_repository.py # Product and category data access
│   │   ├── order_repository.py  # Order data access
│   │   └── payment_repository.py # Payment data access
│   │
│   └── controllers/         # API endpoints (FastAPI routers)
│       ├── __init__.py
│       ├── auth_controller.py    # Authentication endpoints
│       ├── user_controller.py    # User profile endpoints
│       ├── product_controller.py # Product management endpoints
│       ├── order_controller.py   # Order management endpoints
│       └── payment_controller.py # Payment processing endpoints
│
└── requirements.txt         # Python dependencies with versions
