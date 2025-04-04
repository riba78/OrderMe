"""
Admin Routes Module

This module defines all administrative API endpoints for the application.

Endpoints:
1. User Management:
   - GET /api/admin/users: List all users
   - GET /api/admin/users/<id>: Get specific user
   - POST /api/admin/users: Create new user
   - PUT /api/admin/users/<id>: Update user
   - DELETE /api/admin/users/<id>: Delete user

2. Customer Management:
   - GET /api/admin/customers: List all customers
   - POST /api/admin/customers/<id>/activate: Activate customer
   - POST /api/admin/customers/<id>/deactivate: Deactivate customer

Security:
- All routes require admin authentication
- Protected by admin_required decorator
- Prevents self-deletion of admin accounts
- Prevents removal of own admin privileges
"""

from flask import Blueprint, jsonify, request, current_app
from functools import wraps
from models.user import User, UserRole
from models.customer import Customer
from extensions import db
from werkzeug.security import generate_password_hash
from auth.utils import get_current_user, token_required
from enum import Enum

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if not current_user or not current_user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    try:
        print("\n=== Admin Users List Request ===")
        print(f"Request headers: {dict(request.headers)}")
        
        users = User.query.all()
        print(f"Found {len(users)} users")
        
        user_list = []
        for user in users:
            try:
                print(f"\nProcessing user ID: {user.id}")
                print(f"User email: {user.email}")
                print(f"User role: {user.role}")
                user_dict = user.to_dict()
                user_list.append(user_dict)
            except Exception as e:
                print(f"Error processing user {user.id}: {str(e)}")
                continue
        
        return jsonify({"users": user_list})
    except Exception as e:
        print(f"Error in list_users: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get a specific user by ID."""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@admin_bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    """Create a new user with admin privileges."""
    try:
        print("\n=== Create User Request ===")
        data = request.get_json()
        print(f"Request data: {data}")
        
        # Validate required fields
        required_fields = ['email', 'name', 'password', 'role']
        if not all(field in data for field in required_fields):
            missing_fields = [field for field in required_fields if field not in data]
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        # Validate role
        try:
            role = UserRole.coerce(data['role'])
            print(f"Coerced role value: {role}")
        except ValueError as e:
            print(f"Invalid role value: {data['role']}")
            return jsonify({'error': f'Invalid role: {str(e)}'}), 400
        
        # Check if email exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create user
        user = User(
            email=data['email'],
            name=data['name'],
            role=role,  # Use the coerced role enum
            is_verified=True,  # Admin-created users are verified by default
            is_active=data.get('is_active', True),  # Use the active flag from form
            created_by_id=get_current_user().id
        )
        user.set_password(data['password'])
        
        print(f"Creating user with role: {user.role}")
        db.session.add(user)
        db.session.commit()
        
        user_dict = user.to_dict()
        print(f"Created user: {user_dict}")
        return jsonify(user_dict), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating user: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Error creating user: {str(e)}'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update a user's information."""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # Don't allow changing own admin status
    current_user = get_current_user()
    if user.id == current_user.id and 'role' in data and data['role'] != UserRole.ADMIN.value:
        return jsonify({'error': 'Cannot remove own admin privileges'}), 403
    
    # Update fields
    allowed_fields = ['name', 'role', 'is_active']
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])
    
    db.session.commit()
    return jsonify(user.to_dict())

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user from the system."""
    user = User.query.get_or_404(user_id)
    
    # Prevent self-deletion
    current_user = get_current_user()
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot delete own admin account'}), 403
    
    db.session.delete(user)
    db.session.commit()
    return '', 204

@admin_bp.route('/customers', methods=['GET'])
@admin_required
def list_customers():
    try:
        print("\n=== Admin Customers List Request ===")
        print(f"Request headers: {dict(request.headers)}")
        
        customers = User.query.filter_by(role=UserRole.CUSTOMER).all()
        print(f"Found {len(customers)} customers")
        
        customer_list = []
        for customer in customers:
            try:
                print(f"\nProcessing customer ID: {customer.id}")
                print(f"Customer email: {customer.email}")
                print(f"Customer role: {customer.role}")
                customer_dict = customer.to_dict()
                customer_list.append(customer_dict)
            except Exception as e:
                print(f"Error processing customer {customer.id}: {str(e)}")
                continue
        
        return jsonify({"customers": customer_list})
    except Exception as e:
        print(f"Error in list_customers: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500

@admin_bp.route('/customers/<int:customer_id>/activate', methods=['POST'])
@admin_required
def activate_customer(customer_id):
    """Activate a customer account."""
    customer = User.query.get_or_404(customer_id)
    if not customer.is_customer:
        return jsonify({'error': 'User is not a customer'}), 400
    
    customer.is_active = True
    db.session.commit()
    return jsonify(customer.to_dict())

@admin_bp.route('/customers/<int:customer_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_customer(customer_id):
    """Deactivate a customer account."""
    customer = User.query.get_or_404(customer_id)
    if not customer.is_customer:
        return jsonify({'error': 'User is not a customer'}), 400
    
    customer.is_active = False
    db.session.commit()
    return jsonify(customer.to_dict())

@admin_bp.route('/customers/<int:customer_id>', methods=['PUT'])
@admin_required
def update_customer(customer_id):
    """Update a customer's information."""
    customer = User.query.get_or_404(customer_id)
    if not customer.is_customer:
        return jsonify({'error': 'User is not a customer'}), 400
    
    data = request.get_json()
    
    # Update fields
    allowed_fields = ['name', 'email', 'is_active', 'phone_number', 'shipping_address']
    for field in allowed_fields:
        if field in data:
            setattr(customer, field, data[field])
    
    # Update password if provided
    if 'password' in data and data['password']:
        customer.password_hash = generate_password_hash(data['password'])
    
    try:
        db.session.commit()
        return jsonify(customer.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error updating customer: {str(e)}'}), 500

@admin_bp.route('/customers', methods=['POST'])
@admin_required
def create_customer():
    """Create a new customer."""
    print("\n=== Create Customer Request ===")
    data = request.get_json()
    print(f"Request data: {data}")
    
    # Validate required fields
    required_fields = ['email', 'name', 'password']
    if not all(field in data for field in required_fields):
        missing_fields = [field for field in required_fields if field not in data]
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
    
    # Check if email exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    try:
        # Create customer using Customer model
        customer = Customer(
            email=data['email'],
            name=data['name'],
            role=UserRole.CUSTOMER,
            is_verified=True,  # Admin-created customers are verified by default
            is_active=data.get('is_active', True),
            shipping_address=data.get('shipping_address'),
            phone_number=data.get('phone_number'),
            created_by_id=get_current_user().id
        )
        customer.set_password(data['password'])
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify(customer.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating customer: {str(e)}")
        return jsonify({'error': f'Error creating customer: {str(e)}'}), 500