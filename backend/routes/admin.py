"""
Admin Routes Module

This module handles all admin-specific endpoints with:
- User management (CRUD operations)
- Customer management
- Activity monitoring
- System statistics
- Verification tracking
"""

from flask import Blueprint, jsonify, request, g
from models import User, UserRole, UserProfile, VerificationMethod
from models.customer import Customer
from models.activity_log import ActivityLog
from models.verification_message_log import VerificationMessageLog
from auth.decorators import admin_required, token_required
from extensions import db
from datetime import datetime, timedelta
import logging
import uuid
import traceback

admin_bp = Blueprint('admin', __name__)

def get_current_user():
    """Get the current authenticated user directly from Flask g object."""
    return getattr(g, 'current_user', None)

@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """List all users with filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        role = request.args.get('role')
        is_active = request.args.get('is_active', type=lambda x: x.lower() == 'true')
        is_verified = request.args.get('is_verified', type=lambda x: x.lower() == 'true')
        search = request.args.get('search')

        # Build query
        query = User.query

        if role:
            query = query.filter(User.role == UserRole.coerce(role))
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if is_verified is not None:
            query = query.filter(User.is_verified == is_verified)
        if search:
            query = query.join(UserProfile).filter(
                db.or_(
                    User.email.ilike(f'%{search}%'),
                    UserProfile.first_name.ilike(f'%{search}%'),
                    UserProfile.last_name.ilike(f'%{search}%')
                )
            )

        # Execute paginated query
        pagination = query.order_by(User.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        # Log activity
        log_activity(
            user_id=get_current_user().id,
            action_type='list_users',
            metadata={
                'page': page,
                'per_page': per_page,
                'filters': {
                    'role': role,
                    'is_active': is_active,
                    'is_verified': is_verified,
                    'search': search
                }
            }
        )

        return jsonify({
            'users': [user.to_dict(include_profile=True) for user in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        })

    except Exception as e:
        logging.error(f"List users error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get detailed user information"""
    try:
        user = User.query.get_or_404(user_id)

        # Get user's recent activity
        recent_activity = ActivityLog.query.filter_by(
            user_id=user_id
        ).order_by(
            ActivityLog.created_at.desc()
        ).limit(10).all()

        # Get verification history
        verification_history = VerificationMessageLog.query.filter_by(
            user_id=user_id
        ).order_by(
            VerificationMessageLog.created_at.desc()
        ).limit(10).all()

        # Log activity
        log_activity(
            user_id=get_current_user().id,
            action_type='view_user',
            entity_type='user',
            entity_id=user_id
        )

        return jsonify({
            'user': user.to_dict(include_profile=True),
            'recent_activity': [activity.to_dict() for activity in recent_activity],
            'verification_history': [log.to_dict() for log in verification_history]
        })

    except Exception as e:
        logging.error(f"Get user error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@admin_bp.route('/users', methods=['POST'])
@token_required
@admin_required
def create_user():
    """Create a new user with admin privileges."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['email', 'password', 'role']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Check if email exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already registered'}), 400
        
        current_user = get_current_user()
        if not current_user:
            return jsonify({'message': 'Authentication required'}), 401
            
        # Create user
        user = User(
            uuid=str(uuid.uuid4()),
            email=data['email'],
            role=UserRole.coerce(data['role']),
            is_active=True,
            is_verified=True,
            primary_verification_method=data.get('verification_method'),
            created_as_role=current_user.role
        )
        user.set_password(data['password'])
        
        # Create user profile
        profile = UserProfile(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone_number=data.get('phone_number'),
            metadata={'timezone': data.get('timezone'), 'language': data.get('language')}
        )
        user.profile = profile
        
        db.session.add(user)
        db.session.commit()
        
        # Log activity
        try:
            activity = ActivityLog(
                user_id=current_user.id,
                action_type='create_user',
                entity_type='user',
                entity_id=user.id,
                meta_data={'role': data['role']}
            )
            db.session.add(activity)
            db.session.commit()
        except Exception as e:
            logging.error(f"Failed to log activity: {str(e)}")
        
        return jsonify({
            'message': 'User created successfully',
            'id': user.id,
            'uuid': user.uuid,
            'email': user.email
        }), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"User creation error: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': 'Internal server error'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user information"""
    try:
        user = User.query.get_or_404(user_id)
        current_user = get_current_user()
        data = request.json

        # Prevent self-deactivation
        if user.id == current_user.id and data.get('is_active') is False:
            return jsonify({'message': 'Cannot deactivate your own account'}), 400

        # Update user fields
        if 'email' in data and data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'message': 'Email already in use'}), 400
            user.email = data['email']

        if 'role' in data:
            user.role = UserRole.coerce(data['role'])
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'is_verified' in data:
            user.is_verified = data['is_verified']
        if 'verification_method' in data:
            user.primary_verification_method = VerificationMethod.coerce(data['verification_method'])

        # Update profile
        if not user.profile:
            user.profile = UserProfile()

        profile_fields = [
            'first_name', 'last_name', 'phone_number',
            'company_name', 'job_title', 'timezone',
            'language', 'notification_preferences'
        ]

        for field in profile_fields:
            if field in data:
                setattr(user.profile, field, data[field])

        db.session.commit()

        # Log activity
        log_activity(
            user_id=current_user.id,
            action_type='update_user',
            entity_type='user',
            entity_id=user.id,
            metadata={'updated_fields': list(data.keys())}
        )

        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict(include_profile=True)
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Update user error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user"""
    try:
        user = User.query.get_or_404(user_id)
        current_user = get_current_user()

        # Prevent self-deletion
        if user.id == current_user.id:
            return jsonify({'message': 'Cannot delete your own account'}), 400

        # Log activity before deletion
        log_activity(
            user_id=current_user.id,
            action_type='delete_user',
            entity_type='user',
            entity_id=user.id,
            metadata={'email': user.email, 'role': str(user.role)}
        )

        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': 'User deleted successfully'})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Delete user error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@admin_bp.route('/customers', methods=['GET'])
@admin_required
def list_customers():
    """List all customers with filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        is_active = request.args.get('is_active', type=lambda x: x.lower() == 'true')
        search = request.args.get('search')
        assigned_to = request.args.get('assigned_to', type=int)

        # Build query
        query = Customer.query

        if is_active is not None:
            query = query.filter(Customer.is_active == is_active)
        if assigned_to:
            query = query.filter(Customer.assigned_to_id == assigned_to)
        if search:
            query = query.filter(
                db.or_(
                    Customer.email.ilike(f'%{search}%'),
                    Customer.first_name.ilike(f'%{search}%'),
                    Customer.last_name.ilike(f'%{search}%'),
                    Customer.business_name.ilike(f'%{search}%')
                )
            )

        # Execute paginated query
        pagination = query.order_by(Customer.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        # Log activity
        log_activity(
            user_id=get_current_user().id,
            action_type='list_customers',
            metadata={
                'page': page,
                'per_page': per_page,
                'filters': {
                    'is_active': is_active,
                    'search': search,
                    'assigned_to': assigned_to
                }
            }
        )

        return jsonify({
            'customers': [customer.to_dict() for customer in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        })

    except Exception as e:
        logging.error(f"List customers error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@admin_bp.route('/customers/<int:customer_id>', methods=['PUT'])
@admin_required
def update_customer(customer_id):
    """Update customer information"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        current_user = get_current_user()
        data = request.json

        # Update customer fields
        if 'is_active' in data:
            customer.is_active = data['is_active']
        if 'assigned_to_id' in data:
            assigned_to = User.query.get(data['assigned_to_id'])
            if not assigned_to:
                return jsonify({'message': 'Invalid user assignment'}), 400
            customer.assigned_to_id = data['assigned_to_id']
            customer.assigned_at = datetime.utcnow()

        # Update other fields
        updateable_fields = [
            'first_name', 'last_name', 'business_name',
            'phone_number', 'address', 'notes'
        ]

        for field in updateable_fields:
            if field in data:
                setattr(customer, field, data[field])

        db.session.commit()

        # Log activity
        log_activity(
            user_id=current_user.id,
            action_type='update_customer',
            entity_type='customer',
            entity_id=customer.id,
            metadata={'updated_fields': list(data.keys())}
        )

        return jsonify({
            'message': 'Customer updated successfully',
            'customer': customer.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Update customer error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@admin_bp.route('/customers', methods=['POST'])
@token_required
@admin_required
def create_customer():
    """Create a new customer."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['email', 'business_name']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        
        current_user = get_current_user()
        if not current_user:
            return jsonify({'message': 'Authentication required'}), 401
        
        # Create customer
        customer = Customer(
            uuid=str(uuid.uuid4()),
            nickname=data.get('nickname', data['business_name']),
            business_name=data['business_name'],
            email=data['email'],
            phone_number=data.get('phone'),
            assigned_to_id=current_user.id,
            assigned_at=datetime.utcnow(),
            last_assigned_by_id=current_user.id,
            metadata=data.get('metadata', {})
        )
        
        db.session.add(customer)
        db.session.commit()
        
        # Log activity
        try:
            activity = ActivityLog(
                user_id=current_user.id,
                action_type='create_customer',
                entity_type='customer',
                entity_id=customer.id,
                meta_data={'business_name': data['business_name']}
            )
            db.session.add(activity)
            db.session.commit()
        except Exception as e:
            logging.error(f"Failed to log activity: {str(e)}")
        
        return jsonify({
            'message': 'Customer created successfully',
            'id': customer.id,
            'uuid': customer.uuid,
            'business_name': customer.business_name
        }), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Customer creation error: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': 'Internal server error'}), 500

@admin_bp.route('/activity', methods=['GET'])
@token_required
@admin_required
def get_activity_logs():
    """Get activity logs with filtering options."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        user_id = request.args.get('user_id', type=int)
        action_type = request.args.get('action_type')
        
        # Base query
        query = ActivityLog.query
        
        # Apply filters
        if start_date:
            query = query.filter(ActivityLog.created_at >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(ActivityLog.created_at <= datetime.fromisoformat(end_date))
        if user_id:
            query = query.filter(ActivityLog.user_id == user_id)
        if action_type:
            query = query.filter(ActivityLog.action_type == action_type)
        
        # Order by created_at desc
        query = query.order_by(ActivityLog.created_at.desc())
        
        # Explicitly select fields we need without using description which may not exist
        query = query.with_entities(
            ActivityLog.id,
            ActivityLog.created_at,
            ActivityLog.user_id,
            ActivityLog.action_type,
            ActivityLog.entity_type,
            ActivityLog.entity_id,
            ActivityLog.meta_data,
            ActivityLog.ip_address,
            ActivityLog.user_agent
        )
        
        # Paginate results
        pagination = query.paginate(page=page, per_page=per_page)
        
        logs = []
        for log in pagination.items:
            logs.append({
                'id': log.id,
                'created_at': log.created_at.isoformat() if log.created_at else None,
                'user_id': log.user_id,
                'action_type': log.action_type,
                'entity_type': log.entity_type,
                'entity_id': log.entity_id,
                'metadata': log.meta_data,
                'ip_address': log.ip_address,
                'user_agent': log.user_agent
            })
        
        return jsonify({
            'logs': logs,
            'total': pagination.total,
            'pages': pagination.pages,
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        logging.error(f"Activity log retrieval error: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': 'Internal server error'}), 500

@admin_bp.route('/debug-create-user', methods=['POST'])
def debug_create_user():
    """Create a user endpoint for debugging - NO AUTH REQUIRED."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['email', 'password', 'role']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Check if email exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already registered'}), 400
        
        # Create user
        user = User(
            uuid=str(uuid.uuid4()),
            email=data['email'],
            role=data['role'],
            is_active=True,
            is_verified=True,
            primary_verification_method=data.get('verification_method'),
            created_as_role='ADMIN'  # Hardcoded for testing
        )
        user.set_password(data['password'])
        
        # Create user profile
        profile = UserProfile(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone_number=data.get('phone_number'),
            metadata={'timezone': data.get('timezone'), 'language': data.get('language')}
        )
        user.profile = profile
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'id': user.id,
            'uuid': user.uuid,
            'email': user.email
        }), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"User creation debug error: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500

@admin_bp.route('/debug-create-customer', methods=['POST'])
def debug_create_customer():
    """Create a customer endpoint for debugging - NO AUTH REQUIRED."""
    try:
        # Skip customer creation for testing
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        customer_uuid = str(uuid.uuid4())
        
        return jsonify({
            'message': 'Customer created successfully (simulated)',
            'id': 123,  # Simulated ID
            'uuid': customer_uuid,
            'business_name': f"Test Business {timestamp}"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Customer creation debug error: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500

@admin_bp.route('/debug-activity', methods=['GET'])
def debug_activity_logs():
    """Get activity logs without authentication for debugging."""
    try:
        # Create sample activity logs for testing instead of querying the database
        logs = [
            {
                'id': 1,
                'created_at': datetime.utcnow().isoformat(),
                'user_id': 1,
                'action_type': 'login',
                'entity_type': 'user',
                'entity_id': 1,
                'metadata': {'method': 'email'}
            },
            {
                'id': 2,
                'created_at': datetime.utcnow().isoformat(),
                'user_id': 1,
                'action_type': 'view',
                'entity_type': 'customer',
                'entity_id': 123,
                'metadata': {'business_name': 'Test Business'}
            }
        ]
        
        return jsonify({
            'logs': logs,
            'total': len(logs),
            'message': 'Debug activity logs (simulated)'
        })
    except Exception as e:
        logging.error(f"Debug activity log error: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500

def log_activity(user_id: int, action_type: str, entity_type: str = None,
                entity_id: int = None, metadata: dict = None):
    """Log admin activity"""
    try:
        activity = ActivityLog(
            user_id=user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            meta_data=metadata,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string if hasattr(request, 'user_agent') else None
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        logging.error(f"Failed to log activity: {str(e)}")
        db.session.rollback()