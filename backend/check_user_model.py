"""
Script to check the User model in the database
"""
from app import create_app
from models import User
import logging

logging.basicConfig(level=logging.DEBUG)

def check_user_model():
    """Check user model attributes and methods"""
    app = create_app()
    with app.app_context():
        print("Checking User model...")
        try:
            # Get the admin user
            admin_user = User.query.filter_by(email='admin@orderme.com').first()
            print(f"Admin user: {admin_user}")
            print(f"User type: {type(admin_user)}")
            print(f"User columns: {User.__table__.columns.keys()}")
            print(f"Has check_password: {hasattr(admin_user, 'check_password')}")
            print(f"Has verify_password: {hasattr(admin_user, 'verify_password')}")
            print(f"User.__mro__: {[str(c) for c in admin_user.__class__.__mro__]}")
            
            # Check password method
            if hasattr(admin_user, 'check_password'):
                is_valid = admin_user.check_password('admin123')
                print(f"Password check result: {is_valid}")
            
            # Test to_dict method
            try:
                user_dict = admin_user.to_dict()
                print(f"User to_dict: {user_dict}")
            except Exception as e:
                print(f"Error in to_dict: {str(e)}")
                
        except Exception as e:
            print(f"Error checking user model: {str(e)}")

if __name__ == "__main__":
    check_user_model() 