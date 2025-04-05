"""Script to check database schema and display table information."""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://orderme_user:Brat1978@127.0.0.1:3306/orderme')

def check_schema():
    """Check and display database schema information."""
    try:
        # Create database engine
        engine = create_engine(DB_URL)
        
        with engine.connect() as conn:
            # Get all tables (excluding views)
            tables = conn.execute(text("""
                SELECT 
                    table_name,
                    table_rows,
                    ROUND(((data_length + index_length) / 1024 / 1024), 2) as size_mb
                FROM information_schema.tables 
                WHERE table_schema = 'orderme'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)).fetchall()

            print("\nTables in database:")
            print("=" * 60)

            for table in tables:
                print(f"Table: {table[0]}")
                print(f"Rows: {table[1]}")
                print(f"Size: {table[2]:.2f} MB")
                print()

                # Get column information
                columns = conn.execute(text("""
                    SELECT 
                        column_name,
                        column_type,
                        is_nullable,
                        column_key,
                        extra,
                        generation_expression
                    FROM information_schema.columns 
                    WHERE table_schema = 'orderme' 
                    AND table_name = :table
                    ORDER BY ordinal_position
                """), {'table': table[0]}).fetchall()

                print("Columns:")
                print("-" * 40)
                for col in columns:
                    attrs = []
                    if col[2] == 'NO':
                        attrs.append('NOT NULL')
                    if col[3]:  # column_key
                        attrs.append(col[3])
                    if col[4]:  # extra
                        attrs.append(col[4])
                    if col[5]:  # generated column
                        attrs.append('STORED GENERATED')
                    
                    print(f"{col[0]}: {col[1]}" + (f", {', '.join(attrs)}" if attrs else ""))
                print()

                # Get index information
                indexes = conn.execute(text("""
                    SELECT 
                        index_name,
                        GROUP_CONCAT(column_name ORDER BY seq_in_index) as columns
                    FROM information_schema.statistics
                    WHERE table_schema = 'orderme'
                    AND table_name = :table
                    GROUP BY index_name
                    ORDER BY index_name
                """), {'table': table[0]}).fetchall()

                if indexes:
                    print("Indexes:")
                    print("-" * 40)
                    for idx in indexes:
                        print(f"\n{idx[0]}:")
                        for col in idx[1].split(','):
                            print(f"  - Column: {col}")
                    print()

                # Get foreign key information
                foreign_keys = conn.execute(text("""
                    SELECT
                        column_name,
                        referenced_table_name,
                        referenced_column_name
                    FROM information_schema.key_column_usage
                    WHERE table_schema = 'orderme'
                    AND table_name = :table
                    AND referenced_table_name IS NOT NULL
                    ORDER BY column_name
                """), {'table': table[0]}).fetchall()

                if foreign_keys:
                    print("Foreign Keys:")
                    print("-" * 40)
                    for fk in foreign_keys:
                        print(f"{fk[0]} -> {fk[1]}({fk[2]})")
                    print()

                print("=" * 60)
                print()

            # Get all views
            views = conn.execute(text("""
                SELECT 
                    table_name,
                    view_definition
                FROM information_schema.views 
                WHERE table_schema = 'orderme'
                ORDER BY table_name
            """)).fetchall()

            if views:
                print("\nViews in database:")
                print("=" * 60)
                for view in views:
                    print(f"View: {view[0]}")
                    print("\nDefinition:")
                    print("-" * 40)
                    print(view[1])
                    print("\n" + "=" * 60 + "\n")
            else:
                print("\nNo views found in database\n")

    except Exception as e:
        print(f"Error checking schema: {str(e)}")
        raise

if __name__ == '__main__':
    check_schema() 