from sqlalchemy import create_engine, text
from app import create_app
from extensions import db

def drop_all_tables():
    app = create_app()
    with app.app_context():
        # Drop all SQLAlchemy-managed tables
        db.drop_all()
        
        # Drop alembic_version table
        engine = db.get_engine()
        with engine.connect() as conn:
            conn.execute(text('DROP TABLE IF EXISTS alembic_version'))
            conn.commit()
            print("All tables dropped successfully")

if __name__ == '__main__':
    drop_all_tables() 