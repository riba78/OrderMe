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

from flask import Blueprint, jsonify, request
from functools import wraps
from models.user import User, UserRole
from extensions import db
from werkzeug.security import generate_password_hash
from auth.utils import get_current_user, token_required

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
    """List all users in the system."""
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'name', 'password', 'role']
    if not all(field in data for field in required_fields):
        missing_fields = [field for field in required_fields if field not in data]
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
    
    # Validate role
    if data['role'] not in [role.value for role in UserRole]:
        return jsonify({'error': 'Invalid role'}), 400
    
    # Check if email exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    try:
        # Create user
        user = User(
            email=data['email'],
            name=data['name'],
            password_hash=generate_password_hash(data['password']),
            role=data['role'],
            is_verified=True,  # Admin-created users are verified by default
            created_by_id=get_current_user().id
        )
        
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
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
    """List all customers in the system."""
    customers = User.query.filter_by(role=UserRole.CUSTOMER.value).all()
    return jsonify([customer.to_dict() for customer in customers])

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