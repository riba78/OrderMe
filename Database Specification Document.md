# Database Specification Document

This document details the initial database schema, that will be extended in future, for a multi-role system (admin, manager, customer) that manages user profiles, addresses, payment details, products, orders, and order items. The design uses UUIDs for primary keys, is fully normalized, and includes clear relationships, indexes, and constraints for data integrity and performance.

---

## Table of Contents

1. [Overview](#overview)
2. [Table Schemas](#table-schemas)
3. [Relationships](#relationships)
4. [Indexes](#indexes)
5. [Constraints](#constraints)
6. [Conclusion](#conclusion)

---

## Overview

The database consists of the following major tables:

- **Users:** The central table for all user types.
- **Admin_Manager:** Extension for admin and manager users.
- **Customer:** Extension for customer-specific data.
- **User_Profile:** Stores optional profile data (e.g., first name, last name, business name).
- **Address:** Stores optional addresses for users.
- **Payment_Method:** Stores payment method details.
- **Payment_Info:** Stores billing address details related to payment.
- **Products:** Stores product details (created by admin or manager).
- **Orders:** Stores orders placed by customers.
- **Order_Items:** Stores the list of items for each order.

This design adheres to normalization standards and supports scalable application development.

---

## Table Schemas

### 1. Users

```sql
CREATE TABLE Users (
    id CHAR(36) PRIMARY KEY,  -- UUID for global uniqueness
    role ENUM('admin', 'manager', 'customer') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
Purpose: Central user table holding the basic identity and role.
Indexes: Primary key on id (indexed by default).

CREATE TABLE Admin_Manager (
    user_id CHAR(36) PRIMARY KEY,  -- 1:1 relationship with Users
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    verification_method ENUM('email', 'phone', 'WhatsApp') NOT NULL,
    tin_trunk_number VARCHAR(50) DEFAULT NULL,
    CONSTRAINT fk_admin_manager_user FOREIGN KEY (user_id) REFERENCES Users(id)
);
Purpose: Holds authentication and role-specific data for admin and manager users.
Indexes: Primary key on user_id; foreign key column is indexed for joins.

CREATE TABLE Customer (
    user_id CHAR(36) PRIMARY KEY,  -- 1:1 relationship with Users
    phone_number VARCHAR(20) NOT NULL,
    created_by CHAR(36) NOT NULL,    -- ID of creator (admin or manager)
    assigned_manager_id CHAR(36) DEFAULT NULL,  -- Assigned manager; may be NULL
    CONSTRAINT fk_customer_user FOREIGN KEY (user_id) REFERENCES Users(id),
    CONSTRAINT fk_customer_created_by FOREIGN KEY (created_by) REFERENCES Users(id),
    CONSTRAINT fk_customer_assigned_manager FOREIGN KEY (assigned_manager_id) REFERENCES Users(id)
);
Purpose: Contains customer-specific data such as phone number and assignment information.
Indexes: Primary key on user_id; additional indexes on created_by and assigned_manager_id.

CREATE TABLE User_Profile (
    user_id CHAR(36) PRIMARY KEY,  -- 1:1 relationship with Users
    first_name VARCHAR(100) DEFAULT NULL,
    last_name VARCHAR(100) DEFAULT NULL,
    business_name VARCHAR(255) DEFAULT NULL,
    CONSTRAINT fk_profile_user FOREIGN KEY (user_id) REFERENCES Users(id)
);
Purpose: Stores optional profile fields for managers and customers.
Indexes: Primary key on user_id.

CREATE TABLE Address (
    address_id CHAR(36) PRIMARY KEY,  -- UUID for uniqueness
    user_id CHAR(36) NOT NULL,          -- Associated user ID
    street VARCHAR(255) DEFAULT NULL,
    city VARCHAR(100) DEFAULT NULL,
    zip_code VARCHAR(20) DEFAULT NULL,
    contact_phone VARCHAR(20) DEFAULT NULL,
    country VARCHAR(100) DEFAULT NULL,
    CONSTRAINT fk_address_user FOREIGN KEY (user_id) REFERENCES Users(id)
);
Purpose: Stores optional shipping or other addresses for users.
Indexes: Primary key on address_id; index on user_id for faster lookups.

CREATE TABLE Payment_Method (
    id CHAR(36) PRIMARY KEY,  -- UUID for payment method uniqueness
    user_id CHAR(36) NOT NULL,  -- Associated with a manager or customer
    type VARCHAR(50) NOT NULL,  -- e.g., 'credit_card', 'paypal'
    provider VARCHAR(100) NOT NULL,
    last_four VARCHAR(4) NOT NULL,  -- Last four digits
    expiry_date DATE NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_payment_method_user FOREIGN KEY (user_id) REFERENCES Users(id)
);
Purpose: Manages payment method details.
Indexes: Primary key on id; foreign key on user_id is indexed.

CREATE TABLE Payment_Info (
    id CHAR(36) PRIMARY KEY,  -- UUID for payment info record
    user_id CHAR(36) NOT NULL,  -- Associated with a manager or customer
    billing_street VARCHAR(255) NOT NULL,
    billing_city VARCHAR(100) NOT NULL,
    billing_zip VARCHAR(20) NOT NULL,
    billing_country VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_payment_info_user FOREIGN KEY (user_id) REFERENCES Users(id)
);
Purpose: Stores billing address information for payment.
Indexes: Primary key on id; index on user_id.

CREATE TABLE Products (
    product_id CHAR(36) PRIMARY KEY,  -- UUID for product uniqueness
    created_by CHAR(36) NOT NULL,       -- References Users (admin/manager)
    product_name VARCHAR(255) NOT NULL,
    description TEXT,
    qty_in_stock INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    category VARCHAR(100) DEFAULT NULL,  -- Optional
    min_stock_level INT NOT NULL,
    max_stock_level INT NOT NULL,
    last_restock_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_product_creator FOREIGN KEY (created_by) REFERENCES Users(id)
);
Purpose: Stores details about products added by admin or manager.
Indexes: Primary key on product_id; foreign key on created_by.

CREATE TABLE Orders (
    order_id CHAR(36) PRIMARY KEY,  -- UUID for order identification
    user_id CHAR(36) NOT NULL,        -- References Users (customer)
    status ENUM('pending','processing','shipped','delivered','cancelled') NOT NULL,
    total_amount DECIMAL(10,2) DEFAULT NULL,
    shipping_street VARCHAR(255) DEFAULT NULL,
    shipping_city VARCHAR(100) DEFAULT NULL,
    shipping_zip VARCHAR(20) DEFAULT NULL,
    shipping_country VARCHAR(100) DEFAULT NULL,
    tracking_number VARCHAR(100) DEFAULT NULL,
    notes TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_order_user FOREIGN KEY (user_id) REFERENCES Users(id)
);
Purpose: Stores orders placed by customers along with shipping and status details.
Indexes: Primary key on order_id; index on user_id.

CREATE TABLE Order_Items (
    order_item_id CHAR(36) PRIMARY KEY,  -- UUID for each line item
    order_id CHAR(36) NOT NULL,            -- References Orders
    product_id CHAR(36) NOT NULL,          -- References Products
    quantity INT NOT NULL,
    price_at_order DECIMAL(10,2) NOT NULL,  -- Price at the time of order
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) REFERENCES Products(product_id)
);
Purpose: Breaks down orders into individual line items.
Indexes: Primary key on order_item_id; indexes on order_id and product_id for join efficiency.

Relationships

One-to-One Relationships
Users to Admin_Manager:
Each admin/manager has a single corresponding record in the Admin_Manager table.
Users to Customer:
Each customer has a single corresponding record in the Customer table.
Users to User_Profile:
Each user may have one profile record in User_Profile.
One-to-Many Relationships
Users to Address:
A user can have multiple addresses (shipping or otherwise).
Users to Payment_Method / Payment_Info:
A user may have multiple payment methods and billing information records.
Users to Products:
An admin or manager (creator) can add many products.
Users to Orders:
A customer can place multiple orders.
Orders to Order_Items:
An order consists of one or more order items.
Foreign Key Relationships
Each foreign key ensures referential integrity:

Admin_Manager.user_id, Customer.user_id, etc. reference Users.id.
Customer.created_by and Customer.assigned_manager_id reference Users.id.
Products.created_by references Users.id.
Orders.user_id references Users.id.
Order_Items.order_id references Orders.order_id.
Order_Items.product_id references Products.product_id.

Indexes

Primary Key Indexes:
Automatically created on columns defined as PRIMARY KEY (e.g., Users.id, Products.product_id).
Foreign Key Indexes:
It is best practice to index foreign key columns (e.g., user_id in related tables) to optimize join operations.
Additional Indexes:
Depending on query patterns, you might add indexes on frequently filtered columns (e.g., Orders.status).

Constraints

Primary Key Constraints:
Ensure each table’s primary key is unique.
Foreign Key Constraints:
Enforce relationships between tables (e.g., Customer.created_by must reference an existing user in Users).
Not Null Constraints:
Applied to mandatory fields such as Users.role, Admin_Manager.email, Customer.phone_number, etc.
Default Values:
Provide default values for columns such as created_at, updated_at, and active status in Products.
Enumerated Types (ENUM):
Used in columns like Users.role and Orders.status to limit values to a defined set.

