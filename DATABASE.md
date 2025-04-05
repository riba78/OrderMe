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

#### 1. Users Table (Base table for all user types)
```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    uuid CHAR(36) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    primary_verification_method VARCHAR(20),    -- 'email', 'phone', 'whatsapp'
    verification_token VARCHAR(255),
    verification_token_expires DATETIME,
    email_change_token VARCHAR(255),
    email_change_new VARCHAR(120),
    email_change_expires DATETIME,
    last_login_at DATETIME,
    login_count INT DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by_id BIGINT,                      -- Admin who created this user
    created_as_role VARCHAR(20) NOT NULL,      -- Original role at creation
    FOREIGN KEY (created_by_id) REFERENCES users(id),
    CONSTRAINT chk_role CHECK (role IN ('ADMIN', 'USER', 'CUSTOMER')),
    CONSTRAINT chk_verification_method CHECK (primary_verification_method IN ('email', 'phone', 'whatsapp')),
    CONSTRAINT uniq_email_active UNIQUE (email, is_active),
    INDEX idx_uuid (uuid),
    INDEX idx_role (role),
    INDEX idx_verification (verification_token),
    INDEX idx_email_change (email_change_token),
    INDEX idx_created_at (created_at),
    INDEX idx_last_login (last_login_at),
    INDEX idx_created_by (created_by_id, created_as_role)
) ROW_FORMAT=COMPRESSED;

-- Trigger for updated_at
DELIMITER //
CREATE TRIGGER users_before_update
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END //
DELIMITER ;
```

#### 2. User Verification Methods Table (New)
```sql
CREATE TABLE user_verification_methods (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    method_type VARCHAR(20) NOT NULL,          -- 'email', 'phone', 'whatsapp'
    identifier VARCHAR(120) NOT NULL,          -- email or phone number
    verification_token VARCHAR(255),
    token_expires DATETIME,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at DATETIME,
    last_verification_attempt DATETIME,
    verification_attempts INT DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE INDEX idx_user_method (user_id, method_type),
    INDEX idx_identifier (method_type, identifier),
    INDEX idx_token (verification_token)
) ROW_FORMAT=DYNAMIC;
```

#### 2. User Profiles Table (for ADMIN and USER roles)
```sql
CREATE TABLE user_profiles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL UNIQUE,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    business_name VARCHAR(100),
    street VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    zip_code VARCHAR(20),
    country VARCHAR(100),
    phone_number VARCHAR(20),
    tin_trunk_phone VARCHAR(20),
    metadata JSON,                         -- Added for flexible additional data
    search_vector TEXT GENERATED ALWAYS AS (  -- Full-text search optimization
        CONCAT_WS(' ',
            NULLIF(first_name, ''),
            NULLIF(last_name, ''),
            NULLIF(business_name, ''),
            NULLIF(phone_number, '')
        )
    ) STORED,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_profile (user_id),
    INDEX idx_business (business_name),
    INDEX idx_phone (phone_number),
    FULLTEXT INDEX idx_search (search_vector)  -- Full-text search capability
) ROW_FORMAT=DYNAMIC;                      -- Better for variable-length content

-- Partition by creation date for large datasets
PARTITION BY RANGE (UNIX_TIMESTAMP(created_at)) (
    PARTITION p_2024_01 VALUES LESS THAN (UNIX_TIMESTAMP('2024-02-01 00:00:00')),
    PARTITION p_2024_02 VALUES LESS THAN (UNIX_TIMESTAMP('2024-03-01 00:00:00')),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

#### 3. Customers Table (Polymorphic Child)
```sql
CREATE TABLE customers (
    id BIGINT PRIMARY KEY,
    uuid CHAR(36) NOT NULL UNIQUE,         -- Added UUID
    nickname VARCHAR(50) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    business_name VARCHAR(100),
    street VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    zip_code VARCHAR(20),
    country VARCHAR(100),
    email VARCHAR(120),
    phone_number VARCHAR(20),
    metadata JSON,                         -- Flexible additional data
    shipping_address TEXT GENERATED ALWAYS AS (
        CONCAT_WS(', ',
            NULLIF(street, ''),
            NULLIF(city, ''),
            NULLIF(state, ''),
            NULLIF(zip_code, ''),
            NULLIF(country, '')
        )
    ) STORED,
    search_vector TEXT GENERATED ALWAYS AS (  -- Full-text search optimization
        CONCAT_WS(' ',
            NULLIF(nickname, ''),
            NULLIF(first_name, ''),
            NULLIF(last_name, ''),
            NULLIF(business_name, ''),
            NULLIF(email, ''),
            NULLIF(phone_number, '')
        )
    ) STORED,
    assigned_to_id BIGINT NOT NULL,
    assigned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_assigned_by_id BIGINT,
    last_activity_at DATETIME,             -- Track customer activity
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to_id) REFERENCES users(id),
    FOREIGN KEY (last_assigned_by_id) REFERENCES users(id),
    INDEX idx_customer_assignment (assigned_to_id, created_at),  -- Composite index
    INDEX idx_customer_email (email),
    INDEX idx_customer_phone (phone_number),
    INDEX idx_customer_business (business_name),
    INDEX idx_uuid (uuid),
    INDEX idx_last_activity (last_activity_at),
    FULLTEXT INDEX idx_search (search_vector)
) ROW_FORMAT=DYNAMIC
PARTITION BY HASH(assigned_to_id) PARTITIONS 10;  -- Partition by assignment for better query performance
```

#### 4. Activity Logs Table (New)
```sql
CREATE TABLE activity_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    action_type VARCHAR(50) NOT NULL,      -- e.g., 'login', 'profile_update', 'customer_assign'
    entity_type VARCHAR(50) NOT NULL,      -- e.g., 'user', 'customer', 'profile'
    entity_id BIGINT NOT NULL,
    metadata JSON,                         -- Flexible logging data
    ip_address VARCHAR(45),                -- Support for IPv6
    user_agent TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_action (user_id, action_type),
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_created_at (created_at)
) ROW_FORMAT=COMPRESSED
PARTITION BY RANGE (UNIX_TIMESTAMP(created_at)) (
    PARTITION p_last_month VALUES LESS THAN (UNIX_TIMESTAMP('2024-02-01 00:00:00')),
    PARTITION p_current VALUES LESS THAN (UNIX_TIMESTAMP('2024-03-01 00:00:00')),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

#### 5. Verification Messages Log (New)
```sql
CREATE TABLE verification_messages_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    method_type VARCHAR(20) NOT NULL,          -- 'email', 'phone', 'whatsapp'
    message_type VARCHAR(50) NOT NULL,         -- 'verification', 'reset', 'change'
    identifier VARCHAR(120) NOT NULL,          -- email or phone number
    status VARCHAR(20) NOT NULL,               -- 'sent', 'delivered', 'failed'
    provider VARCHAR(50) NOT NULL,             -- 'smtp', 'twilio', 'whatsapp'
    provider_message_id VARCHAR(255),          -- External provider's message ID
    error_message TEXT,                        -- If status is 'failed'
    metadata JSON,                             -- Additional provider-specific data
    ip_address VARCHAR(45),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_method (user_id, method_type),
    INDEX idx_status (status, created_at),
    INDEX idx_provider (provider, created_at)
) ROW_FORMAT=COMPRESSED
PARTITION BY RANGE (UNIX_TIMESTAMP(created_at)) (
    PARTITION p_last_month VALUES LESS THAN (UNIX_TIMESTAMP('2024-02-01 00:00:00')),
    PARTITION p_current VALUES LESS THAN (UNIX_TIMESTAMP('2024-03-01 00:00:00')),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

### Payment-Related Tables

#### 6. Payment Methods Table
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
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_customer_payments (customer_id)
);
```

#### 7. Payment Info Table
```sql
CREATE TABLE payment_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    billing_address TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE INDEX idx_customer_payment_info (customer_id)
);
```

## 3. Key Relationships

### User Creation and Verification Flow

1. **Initial Admin User Creation**
   - Created automatically during first database setup
   - Uses environment variables for credentials:
     * ADMIN_EMAIL (default: admin@orderme.com)
     * ADMIN_PASSWORD (default: admin123)
   - Automatically verified and active
   - No created_by_id (system-created)
   - Has all verification methods enabled
   ```sql
   -- Example: Initial admin user creation
   INSERT INTO users (
       email, 
       password_hash, 
       role,                    -- Set to 'ADMIN'
       is_active,
       is_verified,
       primary_verification_method,
       created_at,
       updated_at
   ) VALUES (
       'admin@orderme.com',
       'hashed_password',
       'ADMIN',                -- Fixed value for initial admin
       TRUE,
       TRUE,
       'email',
       CURRENT_TIMESTAMP,
       CURRENT_TIMESTAMP
   );

   -- Create admin profile
   INSERT INTO user_profiles (
       user_id,
       first_name,
       last_name,
       phone_number
   ) VALUES (
       LAST_INSERT_ID(),
       'Admin',
       'User',
       NULL
   );

   -- Set up verification methods
   INSERT INTO user_verification_methods (
       user_id,
       method_type,
       identifier,
       is_verified,
       verification_token,
       token_expires
   ) VALUES (
       LAST_INSERT_ID(),
       'email',
       'admin@orderme.com',
       TRUE,
       NULL,
       NULL
   );
   ```

2. **Self Registration (Initial Sign Up)**
   - User automatically assigned USER role
   - Required fields: email, password
   - Optional fields during registration:
     * first_name
     * last_name
     * phone_number (for verification)
   ```sql
   -- Example: Self registration process
   INSERT INTO users (
       email, 
       password_hash, 
       role,                    -- Automatically set to 'USER'
       is_active,
       verification_token,
       verification_token_expires,
       primary_verification_method
   ) VALUES (
       'user@example.com',
       'hashed_password',
       'USER',                  -- Fixed value for self-registration
       TRUE,
       'generated_token',
       NOW() + INTERVAL 24 HOUR,
       'email'
   );
   ```

3. **Admin User Creation Capabilities**
   - Can create users with any role (ADMIN, USER, CUSTOMER)
   - Creation tracked through `created_by_id` and `created_as_role`
   - Can set initial verification status
   - Can choose verification method

4. **User Role Creation Capabilities**
   - USER role automatically assigned during self-registration
   - Users can only create CUSTOMER role users after verification
   - Customers automatically assigned to creator
   - Cannot modify customer assignments

5. **Verification Methods**
   ```sql
   -- Example: Setting up multiple verification methods
   INSERT INTO user_verification_methods 
   (user_id, method_type, identifier, verification_token, token_expires)
   VALUES
   (123, 'email', 'user@example.com', 'token123', NOW() + INTERVAL 24 HOUR),
   (123, 'phone', '+1234567890', 'token456', NOW() + INTERVAL 15 MINUTE),
   (123, 'whatsapp', '+1234567890', 'token789', NOW() + INTERVAL 15 MINUTE);
   
   -- Example: Checking verification status
   SELECT 
       u.id,
       u.email,
       u.role,
       u.is_verified,
       u.primary_verification_method,
       GROUP_CONCAT(
           CONCAT(vm.method_type, ':', 
           CASE WHEN vm.is_verified THEN 'verified' ELSE 'pending' END)
       ) as verification_status
   FROM users u
   LEFT JOIN user_verification_methods vm ON u.id = vm.user_id
   WHERE u.id = 123
   GROUP BY u.id;
   ```

6. **Verification Process**
   - Multiple methods can be active simultaneously
   - Each method tracked separately
   - Rate limiting per method
   - Audit trail of all attempts
   - Flexible provider integration

7. **Registration Implementation**
```python
def register_new_user(registration_data):
    """
    Handle new user self-registration process.
    Always creates a USER role account.
    
    Args:
        registration_data: Dict containing registration details
    """
    # Create user with fixed USER role
    user = User(
        email=registration_data['email'],
        role=UserRole.USER,  # Fixed role for self-registration
        is_active=True,
        primary_verification_method=registration_data.get('verification_method', 'email'),
        verification_token=generate_token(),
        verification_token_expires=datetime.utcnow() + timedelta(days=1)
    )
    user.set_password(registration_data['password'])
    db.session.add(user)
    db.session.flush()  # Get user.id
    
    # Create user profile
    profile = UserProfile(
        user_id=user.id,
        first_name=registration_data.get('first_name'),
        last_name=registration_data.get('last_name'),
        phone_number=registration_data.get('phone_number')
    )
    db.session.add(profile)
    
    # Set up verification method(s)
    setup_verification_methods(user, registration_data)
    
    db.session.commit()
    
    # Send verification message
    send_initial_verification(user)
    
    return user

def setup_verification_methods(user, registration_data):
    """Setup verification methods based on provided data."""
    # Always add email verification
    methods = [
        UserVerificationMethod(
            user_id=user.id,
            method_type='email',
            identifier=user.email,
            verification_token=generate_token(),
            token_expires=datetime.utcnow() + timedelta(days=1)
        )
    ]
    
    # Add phone verification if provided
    if phone := registration_data.get('phone_number'):
        methods.append(
            UserVerificationMethod(
                user_id=user.id,
                method_type='phone',
                identifier=phone,
                verification_token=generate_numeric_token(),
                token_expires=datetime.utcnow() + timedelta(minutes=15)
            )
        )
    
    db.session.bulk_save_objects(methods)
```

8. **Registration Flow States**
```sql
-- Example: Tracking registration states
SELECT 
    u.id,
    u.email,
    u.role,                     -- Will be 'USER' for self-registration
    u.is_verified,
    u.primary_verification_method,
    up.first_name,
    up.last_name,
    GROUP_CONCAT(
        CONCAT(vm.method_type, ':', 
        CASE WHEN vm.is_verified THEN 'verified' ELSE 'pending' END)
    ) as verification_status
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
LEFT JOIN user_verification_methods vm ON u.id = vm.user_id
WHERE u.created_by_id IS NULL  -- Self-registered users
GROUP BY u.id;
```

### User Profile Management
1. **Profile Creation**
   - Created automatically with user registration
   - Initially contains only required fields
   - Can be updated progressively

2. **Profile Fields**
   - Personal: first_name, last_name
   - Business: business_name
   - Contact: phone_number, tin_trunk_phone
   - Address: street, city, state, zip_code, country

### Customer Management
1. **Customer Creation**
   - Created with nickname (required)
   - Automatically assigned to creator
   - Assignment rules:
     * User role: Customer locked to creator
     * Admin role: Can reassign customer

2. **Customer Fields**
   - Identity: nickname, first_name, last_name
   - Business: business_name
   - Contact: email, phone_number
   - Location: street, city, state, zip_code, country
   - Generated: shipping_address (computed from address fields)

3. **Assignment Tracking**
   - assigned_to_id: Current owner
   - assigned_at: Last assignment time
   - last_assigned_by_id: Last admin who changed assignment

## 4. Implementation Requirements

### User Creation
```python
def create_user(creator, new_user_data):
    """
    Create a new user with specified role and verification method.
    
    Args:
        creator: User object of the creating admin/user
        new_user_data: Dict containing user details and verification preferences
    """
    # Verify creator has permission for the requested role
    if new_user_data['role'] != UserRole.CUSTOMER and not creator.is_admin:
        raise PermissionError("Only admins can create non-customer users")
    
    # Create user
    user = User(
        email=new_user_data['email'],
        role=new_user_data['role'],
        created_by_id=creator.id,
        created_as_role=new_user_data['role'],
        primary_verification_method=new_user_data['verification_method']
    )
    db.session.add(user)
    db.session.flush()  # Get user.id
    
    # Set up verification methods
    for method in new_user_data['verification_methods']:
        verification = UserVerificationMethod(
            user_id=user.id,
            method_type=method['type'],
            identifier=method['identifier'],
            verification_token=generate_token(),
            token_expires=datetime.utcnow() + get_token_expiry(method['type'])
        )
        db.session.add(verification)
        
        # Send verification message
        send_verification(
            method_type=method['type'],
            identifier=method['identifier'],
            token=verification.verification_token
        )
    
    db.session.commit()
    return user
```

### Customer Assignment
```python
def reassign_customer(customer_id, new_user_id, admin_user):
    if not admin_user.is_admin:
        raise PermissionError("Only admins can reassign customers")
    
    customer = Customer.query.get(customer_id)
    customer.assigned_to_id = new_user_id
    customer.assigned_at = datetime.utcnow()
    customer.last_assigned_by_id = admin_user.id
```

### Email Change Process
```python
def initiate_email_change(user, new_email):
    user.email_change_new = new_email
    user.email_change_token = generate_token()
    user.email_change_expires = datetime.utcnow() + timedelta(days=1)
    # Send verification email
```

## 5. Security Considerations

### Email Verification
- Tokens must be cryptographically secure
- Tokens must have expiration
- Old tokens must be invalidated on success
- Rate limiting on verification attempts

### Profile Updates
- Validate all input fields
- Sanitize business and address fields
- Verify phone number formats
- Maintain update history for auditing

### Customer Assignment
- Enforce role-based assignment rules
- Log all assignment changes
- Notify relevant users of changes
- Maintain assignment history

### Additional Security Considerations

1. **Verification Rate Limiting**
   - Limit attempts per method
   - Exponential backoff for failures
   - IP-based rate limiting
   - Device fingerprinting

2. **Message Security**
   - Secure token generation
   - Short-lived tokens
   - Provider-specific security
   - Message delivery tracking

3. **Audit Requirements**
   - Log all verification attempts
   - Track message delivery status
   - Monitor unusual patterns
   - Alert on suspicious activity

### Self-Registration Security
   - Rate limiting by IP address
   - Email domain validation
   - Password strength requirements
   - Captcha/robot verification
   - Duplicate email prevention

### Verification Requirements
   - Must verify email or phone before full access
   - Limited functionality until verified
   - Configurable verification timeout
   - Multiple verification attempts tracking

## 6. Scalability Features

### 1. High-Volume Data Handling
- BIGINT for IDs to support large number of records
- UUID for public references (avoid exposing sequential IDs)
- Table partitioning for better query performance
- Compressed row format for storage efficiency
- Proper indexing strategy for large datasets

### 2. Search Optimization
- Computed search vectors for full-text search
- Composite indexes for common query patterns
- Metadata JSON fields for flexible data storage
- Partitioned tables for faster searches
- Optimized index coverage for frequent queries

### 3. Performance Features
- Activity tracking for analytics
- Efficient date-based partitioning
- Composite indexes for common joins
- Compressed tables for large datasets
- Optimized row formats per table type

### 4. Monitoring and Analytics
- Login tracking
- Activity logging
- Flexible metadata storage
- Customer activity tracking
- Assignment history preservation

### 5. Data Integrity at Scale
- Foreign key constraints with proper indexes
- Unique constraints for critical fields
- Computed fields for consistency
- Activity logging for auditing
- Proper constraint naming for maintenance

### 6. Query Optimization
```sql
-- Example: Efficient customer search
SELECT c.* FROM customers c
WHERE MATCH(c.search_vector) AGAINST ('+john +doe' IN BOOLEAN MODE)
  AND c.assigned_to_id = 123;

-- Example: Active users in date range
SELECT u.* FROM users u
FORCE INDEX (idx_last_login)
WHERE u.last_login_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
  AND u.is_active = 1;

-- Example: Customer assignment history
SELECT al.* FROM activity_logs al
WHERE al.entity_type = 'customer'
  AND al.action_type = 'customer_assign'
  AND al.entity_id = 456
ORDER BY al.created_at DESC;
```

### Migration Process

1. **Database Setup**
   ```sql
   -- Create database if not exists
   CREATE DATABASE IF NOT EXISTS orderme CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   
   -- Create user if not exists
   CREATE USER IF NOT EXISTS 'orderme_user'@'localhost' IDENTIFIED BY 'Brat1978';
   
   -- Grant privileges
   GRANT ALL PRIVILEGES ON orderme.* TO 'orderme_user'@'localhost';
   FLUSH PRIVILEGES;
   
   USE orderme;
   ```

2. **Table Creation**
   ```sql
   -- Drop existing tables if they exist
   DROP TABLE IF EXISTS user_verification_methods;
   DROP TABLE IF EXISTS user_profiles;
   DROP TABLE IF EXISTS customers;
   DROP TABLE IF EXISTS users;
   
   -- Create users table
   CREATE TABLE users (
       id INT AUTO_INCREMENT PRIMARY KEY,
       email VARCHAR(120) UNIQUE NOT NULL,
       name VARCHAR(120) NOT NULL,
       password_hash VARCHAR(255) NOT NULL,
       role VARCHAR(20) NOT NULL,
       is_active BOOLEAN NOT NULL DEFAULT TRUE,
       is_verified BOOLEAN NOT NULL DEFAULT FALSE,
       primary_verification_method VARCHAR(20) NOT NULL DEFAULT 'email',
       created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
       updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
       created_by_id INT,
       FOREIGN KEY (created_by_id) REFERENCES users(id)
   );
   
   -- Create other tables...
   ```

3. **Initial Data Setup**
   ```sql
   -- Create initial admin user
   INSERT INTO users (
       email, 
       password_hash, 
       role, 
       is_active, 
       is_verified,
       primary_verification_method
   ) VALUES (
       'admin@orderme.com',
       'pbkdf2:sha256:1000000$1VWiDFjgXyjtfMKA$81cc2096aceaba939ec945e7e8270142c10b8a9cc32e63b4a4bdb5637cc413e9',
       'ADMIN',
       TRUE,
       TRUE,
       'email'
   );
   
   -- Create admin profile
   INSERT INTO user_profiles (
       user_id,
       first_name,
       last_name,
       phone_number
   ) VALUES (
       LAST_INSERT_ID(),
       'Admin',
       'User',
       NULL
   );
   
   -- Set up admin verification methods
   INSERT INTO user_verification_methods (
       user_id,
       method_type,
       identifier,
       is_verified,
       verification_token,
       token_expires
   ) VALUES (
       LAST_INSERT_ID(),
       'email',
       'admin@orderme.com',
       TRUE,
       NULL,
       NULL
   );
   ```

4. **Migration Script**
   ```python
   def migrate_database():
       """Handle database migration and initial setup."""
       try:
           # Create tables
           db.create_all()
           
           # Check for admin user
           admin = User.query.filter_by(email='admin@orderme.com').first()
           if not admin:
               # Create admin user
               admin = User(
                   email='admin@orderme.com',
                   name='Admin User',
                   role=UserRole.ADMIN,
                   is_verified=True,
                   is_active=True,
                   primary_verification_method='email'
               )
               admin.set_password('admin123')
               db.session.add(admin)
               db.session.flush()  # Get admin.id
               
               # Create admin profile
               profile = UserProfile(
                   user_id=admin.id,
                   first_name='Admin',
                   last_name='User'
               )
               db.session.add(profile)
               
               # Set up verification methods
               verification = UserVerificationMethod(
                   user_id=admin.id,
                   method_type='email',
                   identifier='admin@orderme.com',
                   is_verified=True
               )
               db.session.add(verification)
               
               db.session.commit()
               print("Initial admin user created successfully")
           
           print("Database migration completed successfully")
           
       except Exception as e:
           db.session.rollback()
           print(f"Migration error: {str(e)}")
           raise
   ```

This documentation reflects the current state of the database structure and serves as a reference for development and maintenance.

### Database Views

#### 1. Active Users View
```sql
CREATE VIEW v_active_users AS
SELECT 
    u.id,
    u.email,
    u.role,
    u.is_verified,
    u.last_login_at,
    up.first_name,
    up.last_name,
    up.phone_number
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
WHERE u.is_active = TRUE;
```

#### 2. Customer Assignment History View
```sql
CREATE VIEW v_customer_assignments AS
SELECT 
    c.id AS customer_id,
    c.nickname,
    c.email,
    c.phone_number,
    u1.id AS assigned_to_id,
    u1.email AS assigned_to_email,
    u2.id AS assigned_by_id,
    u2.email AS assigned_by_email,
    c.assigned_at,
    c.last_activity_at
FROM customers c
JOIN users u1 ON c.assigned_to_id = u1.id
LEFT JOIN users u2 ON c.last_assigned_by_id = u2.id;
```

### Stored Procedures

#### 1. User Creation Procedure
```sql
DELIMITER //
CREATE PROCEDURE sp_create_user(
    IN p_email VARCHAR(120),
    IN p_password VARCHAR(255),
    IN p_role VARCHAR(20),
    IN p_created_by_id BIGINT,
    IN p_verification_method VARCHAR(20),
    OUT p_user_id BIGINT
)
BEGIN
    DECLARE v_uuid CHAR(36);
    SET v_uuid = UUID();
    
    INSERT INTO users (
        uuid,
        email,
        password_hash,
        role,
        created_by_id,
        created_as_role,
        primary_verification_method
    ) VALUES (
        v_uuid,
        p_email,
        p_password,
        p_role,
        p_created_by_id,
        p_role,
        p_verification_method
    );
    
    SET p_user_id = LAST_INSERT_ID();
    
    -- Log the creation
    INSERT INTO activity_logs (
        user_id,
        action_type,
        entity_type,
        entity_id,
        metadata
    ) VALUES (
        p_created_by_id,
        'user_create',
        'user',
        p_user_id,
        JSON_OBJECT('role', p_role, 'verification_method', p_verification_method)
    );
END //
DELIMITER ;
```

#### 2. Customer Assignment Procedure
```sql
DELIMITER //
CREATE PROCEDURE sp_assign_customer(
    IN p_customer_id BIGINT,
    IN p_new_user_id BIGINT,
    IN p_assigned_by_id BIGINT
)
BEGIN
    DECLARE v_old_user_id BIGINT;
    
    -- Get current assignment
    SELECT assigned_to_id INTO v_old_user_id
    FROM customers
    WHERE id = p_customer_id;
    
    -- Update assignment
    UPDATE customers
    SET 
        assigned_to_id = p_new_user_id,
        assigned_at = CURRENT_TIMESTAMP,
        last_assigned_by_id = p_assigned_by_id
    WHERE id = p_customer_id;
    
    -- Log the change
    INSERT INTO activity_logs (
        user_id,
        action_type,
        entity_type,
        entity_id,
        metadata
    ) VALUES (
        p_assigned_by_id,
        'customer_assign',
        'customer',
        p_customer_id,
        JSON_OBJECT(
            'old_user_id', v_old_user_id,
            'new_user_id', p_new_user_id
        )
    );
END //
DELIMITER ;
```

### Database Functions

#### 1. Phone Number Validation
```sql
DELIMITER //
CREATE FUNCTION fn_validate_phone(phone VARCHAR(20))
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    RETURN phone REGEXP '^\\+?[1-9]\\d{1,14}$';
END //
DELIMITER ;
```

#### 2. Email Validation
```sql
DELIMITER //
CREATE FUNCTION fn_validate_email(email VARCHAR(120))
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    RETURN email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$';
END //
DELIMITER ;
```