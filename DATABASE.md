# OrderMe Database Documentation

## 1. User Role System and Polymorphism

### User Roles
The system implements a role-based access control system with three distinct roles:
```python
class UserRole(str, Enum):
    ADMIN = 'ADMIN'    # Full system access
    USER = 'USER'      # Customer management access
    CUSTOMER = 'CUSTOMER'  # Limited access
```

### Polymorphic Inheritance
The system uses SQLAlchemy's polymorphic inheritance to handle different user types:

1. **Base User Model** (`users` table)
   - Acts as the parent table for all user types
   - Uses `role` column as the discriminator
   - Default polymorphic identity: 'user'

2. **Customer Model** (`customers` table)
   - Inherits from User model
   - Polymorphic identity: 'CUSTOMER'
   - Adds customer-specific fields

## 2. Database Schema

### Core Tables

#### 1. Users Table
```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(120) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    tin_trunk_phone VARCHAR(20) NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    created_by_id INT,
    FOREIGN KEY (created_by_id) REFERENCES users(id)
);
```

#### 2. Customers Table (Polymorphic Child)
```sql
CREATE TABLE customers (
    id INT PRIMARY KEY,
    shipping_address TEXT NULL,
    phone_number VARCHAR(20) NULL,
    assigned_to_id INT,
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to_id) REFERENCES users(id)
);
```

### Payment-Related Tables

#### 3. Payment Methods Table
```sql
CREATE TABLE payment_methods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    type VARCHAR(50) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    last_four VARCHAR(4) NOT NULL,
    expiry_date DATETIME NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### 4. Payment Info Table
```sql
CREATE TABLE payment_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    billing_address TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## 3. Key Relationships

### User Hierarchy
1. **Admin Users**
   - Can manage all users
   - Can create any type of user
   - Full system access

2. **Regular Users**
   - Can manage only customers
   - Can create only customer accounts
   - Limited system access

3. **Customers**
   - No management privileges
   - Can only access their own data
   - Can be assigned to regular users

### Customer Assignment
- Customers can be assigned to regular users or admins
- Assignment is tracked through `assigned_to_id` in customers table
- Automatic assignment when a regular user creates a customer

### Payment Relationships
- Each customer can have multiple payment methods
- One payment method can be set as default
- Each customer can have one payment info record
- All payment records are deleted when a customer is deleted (CASCADE)

## 4. Key Features

### Security
- Passwords are hashed using Werkzeug's `generate_password_hash`
- Uses `pbkdf2:sha256` method for password hashing
- Password hash format: `pbkdf2:sha256:iterations$salt$hash`
- Default iteration count is 1000000 for enhanced security
- Never store plain text passwords
- Use parameterized queries
- Implement proper access controls

### Audit Trail
- All tables include `created_at`