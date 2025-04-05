from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

# Database URL configuration
db_url = os.getenv('DATABASE_URL', 'mysql+pymysql://orderme_user:Brat1978@127.0.0.1:3306/orderme')

def check_users():
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, email, role, is_active, is_verified, primary_verification_method 
            FROM users
        """))
        for row in result:
            print(row)

if __name__ == '__main__':
    check_users() 