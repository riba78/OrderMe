from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database configuration
DB_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://orderme_user:Brat1978@127.0.0.1:3306/orderme')

def check_admin():
    """Check if admin user exists and print their details."""
    engine = create_engine(DB_URL)
    
    with engine.connect() as conn:
        # Check admin user
        result = conn.execute(text("""
            SELECT 
                u.id,
                u.uuid,
                u.email,
                u.role,
                u.is_verified,
                up.first_name,
                up.last_name,
                uvm.method_type as verification_method,
                uvm.is_verified as method_verified
            FROM users u
            LEFT JOIN user_profiles up ON u.id = up.user_id
            LEFT JOIN user_verification_methods uvm ON u.id = uvm.user_id
            WHERE u.role = UserRole.ADMIN.value
        """)).fetchall()
        
        if result:
            print("\nAdmin users found:")
            for row in result:
                print(f"\nUser ID: {row[0]}")
                print(f"UUID: {row[1]}")
                print(f"Email: {row[2]}")
                print(f"Role: {row[3]}")
                print(f"Is Verified: {row[4]}")
                print(f"First Name: {row[5]}")
                print(f"Last Name: {row[6]}")
                print(f"Verification Method: {row[7]}")
                print(f"Method Verified: {row[8]}")
        else:
            print("\nNo admin users found in the database")

if __name__ == '__main__':
    check_admin() 