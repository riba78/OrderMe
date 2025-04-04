from extensions import db
from models.user import User
from models.customer import Customer
from sqlalchemy.schema import CreateTable

def show_table_sql():
    # Show Users table
    print("\n=== Users Table SQL ===")
    print(CreateTable(User.__table__))
    
    # Show Customers table
    print("\n=== Customers Table SQL ===")
    print(CreateTable(Customer.__table__))

if __name__ == "__main__":
    show_table_sql() 