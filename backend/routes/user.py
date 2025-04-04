"""
User Routes Module

This module defines all user-specific API endpoints for the application.
"""

from flask import Blueprint, jsonify, request
from models.user import User, UserRole
from models.customer import Customer
from auth.utils import get_current_user, token_required
from datetime import datetime, timedelta
from sqlalchemy import func
from extensions import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/stats', methods=['GET'])
@token_required
def get_dashboard_stats():
    """Get dashboard statistics."""
    try:
        print("\n=== Dashboard Stats Request ===")
        
        # Get total and active customers
        total_customers = Customer.query.count()
        active_customers = Customer.query.filter_by(is_active=True).count()
        
        # For now, return basic stats (orders will be implemented later)
        stats = {
            "totalCustomers": total_customers,
            "activeCustomers": active_customers,
            "totalOrders": 0,  # Will be implemented with orders feature
            "pendingOrders": 0,  # Will be implemented with orders feature
            "totalRevenue": 0.00  # Will be implemented with orders feature
        }
        
        print(f"Stats: {stats}")
        return jsonify(stats)
        
    except Exception as e:
        print(f"Error getting dashboard stats: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/orders/recent', methods=['GET'])
@token_required
def get_recent_orders():
    """Get recent orders."""
    try:
        # Will be implemented with orders feature
        return jsonify([])
    except Exception as e:
        print(f"Error getting recent orders: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500 