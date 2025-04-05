"""
User Routes Module

This module handles user-specific endpoints with:
- User profile management
- Dashboard statistics
- Recent activity tracking
- User preferences
"""

from flask import Blueprint, jsonify, request
from models.user import User, UserProfile
from models.customer import Customer
from models.activity_log import ActivityLog
from models.verification_message_log import VerificationMessageLog
from auth.decorators import token_required, get_current_user
from extensions import db
from datetime import datetime, timedelta
import logging

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get current user's profile"""
    try:
        user = get_current_user()
        return jsonify({
            'user': user.to_dict(include_profile=True)
        })
    except Exception as e:
        logging.error(f"Get profile error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    """Update current user's profile"""
    try:
        user = get_current_user()
        data = request.json

        # Update profile fields
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

        # Update email if provided and different
        new_email = data.get('email')
        if new_email and new_email != user.email:
            # Check if email is already in use
            if User.query.filter_by(email=new_email).first():
                return jsonify({'message': 'Email already in use'}), 400
            
            # Initiate email change process
            user.initiate_email_change(new_email)

        db.session.commit()

        # Log profile update
        log_activity(
            user_id=user.id,
            action_type='profile_update',
            metadata={'updated_fields': list(data.keys())}
        )

        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict(include_profile=True)
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Update profile error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@user_bp.route('/stats', methods=['GET'])
@token_required
def get_stats():
    """Get user's dashboard statistics"""
    try:
        user = get_current_user()
        
        # Get basic stats
        total_customers = Customer.query.filter_by(created_by_id=user.id).count()
        active_customers = Customer.query.filter_by(
            created_by_id=user.id,
            is_active=True
        ).count()

        # Get recent activity
        recent_activity = ActivityLog.query.filter_by(
            user_id=user.id
        ).order_by(
            ActivityLog.created_at.desc()
        ).limit(10).all()

        # Get verification stats
        verification_stats = db.session.query(
            VerificationMessageLog.status,
            db.func.count(VerificationMessageLog.id)
        ).filter(
            VerificationMessageLog.user_id == user.id,
            VerificationMessageLog.created_at >= datetime.utcnow() - timedelta(days=30)
        ).group_by(
            VerificationMessageLog.status
        ).all()

        return jsonify({
            'customers': {
                'total': total_customers,
                'active': active_customers
            },
            'recent_activity': [activity.to_dict() for activity in recent_activity],
            'verification_stats': dict(verification_stats)
        })

    except Exception as e:
        logging.error(f"Get stats error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@user_bp.route('/preferences', methods=['PUT'])
@token_required
def update_preferences():
    """Update user preferences"""
    try:
        user = get_current_user()
        data = request.json

        if not user.profile:
            user.profile = UserProfile()

        # Update notification preferences
        if 'notification_preferences' in data:
            user.profile.notification_preferences = data['notification_preferences']

        # Update timezone
        if 'timezone' in data:
            user.profile.timezone = data['timezone']

        # Update language
        if 'language' in data:
            user.profile.language = data['language']

        db.session.commit()

        # Log preferences update
        log_activity(
            user_id=user.id,
            action_type='preferences_update',
            metadata={'updated_preferences': list(data.keys())}
        )

        return jsonify({
            'message': 'Preferences updated successfully',
            'preferences': {
                'notification_preferences': user.profile.notification_preferences,
                'timezone': user.profile.timezone,
                'language': user.profile.language
            }
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Update preferences error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

def log_activity(user_id: int, action_type: str, metadata: dict = None):
    """Log user activity"""
    try:
        activity = ActivityLog(
            user_id=user_id,
            action_type=action_type,
            metadata=metadata,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        logging.error(f"Failed to log activity: {str(e)}") 