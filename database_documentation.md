# Database and API Documentation

## Database Models

### Base Model
All models inherit from `Base` and `TimestampMixing` which provides:
- UUID primary keys
- Created/Updated timestamps
- Async ORM support
- Consistent naming conventions for constraints

### Core Models

#### User (`users` table)
- Primary model for all system users
- Fields:
  - `id`: UUID (PK)
  - `role`: Enum (admin, manager, customer)
  - `is_active`: Boolean
  - `created_at`: DateTime
  - `updated_at`: DateTime

#### Customer (`customers` table)
- Extension of User model for customer-specific data
- Fields:
  - `id`: UUID (PK, FK to users.id)
  - `phone`: String(20)
  - `created_by`: UUID (FK to users.id)
  - `assigned_manager_id`: UUID (FK to users.id, nullable)
  - `created_at`: DateTime
  - `updated_at`: DateTime

#### AdminManager (`admin_managers` table)
- Extension of User model for admin/manager authentication
- Fields:
  - `id`: UUID (PK, FK to users.id)
  - `email`: String(255), unique
  - `password_hash`: String(255)
  - `tin_trunk_number`: String(50), nullable
  - `verification_method`: Enum (whatsapp, email, phone)
  - `created_at`: DateTime
  - `updated_at`: DateTime

### Relationships

1. User -> AdminManager (One-to-One)
   - One User can have one AdminManager profile
   - Relationship: `user.admin_manager` ↔ `admin_manager.user`

2. User -> Customer (One-to-One)
   - One User can have one Customer profile
   - Relationship: `user.customer` ↔ `customer.user`

3. User -> Created Customers (One-to-Many)
   - One User (admin/manager) can create many Customers
   - Relationship: `user.created_customers` ↔ `customer.create_by_user`

4. User -> Assigned Customers (One-to-Many)
   - One User (manager) can be assigned many Customers
   - Relationship: `user.assigned_customers` ↔ `customer.assigned_manager`

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/signup`: Create new user account
- `POST /auth/signin`: Authenticate and get access token

### Users (`/users`)
- `GET /users/`: List all users (role-based access)
- `GET /users/me`: Get current user profile
- `GET /users/managed-customers/`: List customers managed by current manager
- `POST /users/`: Create new user (role-based access)

## Role-Based Access Control

### User Roles
1. Admin
   - Full system access
   - Can create/manage all users
   - Can view all customers

2. Manager
   - Can manage assigned customers
   - Can view only assigned customers
   - Limited user management capabilities

3. Customer
   - Basic user access
   - Can view own profile
   - Limited to customer-specific operations

## Data Flow
1. Authentication Flow:
   - User signs up/signs in
   - System validates credentials
   - Returns JWT token for subsequent requests

2. User Management Flow:
   - Admin/Manager creates user
   - System creates base User record
   - Based on role, creates corresponding profile (AdminManager/Customer)
   - Assigns relationships (created_by, assigned_manager)

3. Customer Management Flow:
   - Manager can view assigned customers
   - Manager can update customer information
   - System enforces role-based access control 