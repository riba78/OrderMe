-- Create database if not exists
CREATE DATABASE IF NOT EXISTS orderme;

-- Create user if not exists
CREATE USER IF NOT EXISTS 'orderme_user'@'localhost' IDENTIFIED BY 'Brat1978';

-- Grant privileges
GRANT ALL PRIVILEGES ON orderme.* TO 'orderme_user'@'localhost';
FLUSH PRIVILEGES;

-- Use the database
USE orderme;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS payment_info;
DROP TABLE IF EXISTS payment_methods;
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
    tin_trunk_phone VARCHAR(20) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by_id INT,
    FOREIGN KEY (created_by_id) REFERENCES users(id)
);

-- Create customers table
CREATE TABLE customers (
    id INT PRIMARY KEY,
    shipping_address TEXT NULL,
    phone_number VARCHAR(20) NULL,
    assigned_to_id INT,
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to_id) REFERENCES users(id)
);

-- Create payment_methods table
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

-- Create payment_info table
CREATE TABLE payment_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    billing_address TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create admin user
-- Password: admin123 (hashed using Werkzeug's generate_password_hash)
INSERT INTO users (email, name, password_hash, role, is_active, is_verified, created_at, updated_at)
VALUES (
    'admin@orderme.com',
    'Admin User',
    'pbkdf2:sha256:1000000$1VWiDFjgXyjtfMKA$81cc2096aceaba939ec945e7e8270142c10b8a9cc32e63b4a4bdb5637cc413e9',
    'ADMIN',
    TRUE,
    TRUE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
); 