"""Update schema to match DATABASE.md

Revision ID: update_schema_to_match_docs
Revises: 
Create Date: 2024-04-05

This migration updates the database schema to match the specifications in DATABASE.md
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.sql import text

# revision identifiers, used by Alembic
revision = 'update_schema_to_match_docs'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Update customers table
    with op.batch_alter_table('customers') as batch_op:
        # Add new columns
        batch_op.add_column(sa.Column('nickname', sa.String(50), nullable=False))
        batch_op.add_column(sa.Column('business_name', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('city', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('state', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('zip_code', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('country', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('metadata', sa.JSON, nullable=True))
        batch_op.add_column(sa.Column('last_activity_at', sa.DateTime, nullable=True))
        
        # Rename columns
        batch_op.alter_column('last_assigned_at', new_column_name='assigned_at')
        
        # Add computed columns
        batch_op.execute("""
        ALTER TABLE customers 
        ADD COLUMN shipping_address TEXT GENERATED ALWAYS AS (
            CONCAT_WS(', ',
                NULLIF(address, ''),
                NULLIF(city, ''),
                NULLIF(state, ''),
                NULLIF(zip_code, ''),
                NULLIF(country, '')
            )
        ) STORED;
        """)
        
        batch_op.execute("""
        ALTER TABLE customers 
        ADD COLUMN search_vector TEXT GENERATED ALWAYS AS (
            CONCAT_WS(' ',
                NULLIF(nickname, ''),
                NULLIF(first_name, ''),
                NULLIF(last_name, ''),
                NULLIF(business_name, ''),
                NULLIF(email, ''),
                NULLIF(phone, '')
            )
        ) STORED;
        """)
        
        # Add indexes
        batch_op.create_index('idx_customer_assignment', ['assigned_to_id', 'created_at'])
        batch_op.create_index('idx_customer_email', ['email'])
        batch_op.create_index('idx_customer_phone', ['phone'])
        batch_op.create_index('idx_customer_business', ['business_name'])
        batch_op.create_index('idx_last_activity', ['last_activity_at'])
        batch_op.create_fulltext_index('idx_search', ['search_vector'])

    # Update user_profiles table
    with op.batch_alter_table('user_profiles') as batch_op:
        # Add new columns
        batch_op.add_column(sa.Column('first_name', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('last_name', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('business_name', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('street', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('city', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('state', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('zip_code', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('country', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('phone_number', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('tin_trunk_phone', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('metadata', sa.JSON, nullable=True))
        
        # Add computed column
        batch_op.execute("""
        ALTER TABLE user_profiles 
        ADD COLUMN search_vector TEXT GENERATED ALWAYS AS (
            CONCAT_WS(' ',
                NULLIF(first_name, ''),
                NULLIF(last_name, ''),
                NULLIF(business_name, ''),
                NULLIF(phone_number, '')
            )
        ) STORED;
        """)
        
        # Add indexes
        batch_op.create_index('idx_business', ['business_name'])
        batch_op.create_index('idx_phone', ['phone_number'])
        batch_op.create_fulltext_index('idx_search', ['search_vector'])

    # Update activity_logs table
    with op.batch_alter_table('activity_logs') as batch_op:
        # Rename column
        batch_op.alter_column('activity_type', new_column_name='action_type')
        
        # Add new columns
        batch_op.add_column(sa.Column('entity_type', sa.String(50), nullable=False))
        batch_op.add_column(sa.Column('entity_id', sa.BigInteger, nullable=False))
        batch_op.add_column(sa.Column('metadata', sa.JSON, nullable=True))
        
        # Add indexes
        batch_op.create_index('idx_user_action', ['user_id', 'action_type'])
        batch_op.create_index('idx_entity', ['entity_type', 'entity_id'])
        batch_op.create_index('idx_created_at', ['created_at'])

    # Update verification_messages_log table
    with op.batch_alter_table('verification_messages_log') as batch_op:
        # Rename column
        batch_op.alter_column('sent_to', new_column_name='identifier')
        
        # Add new columns
        batch_op.add_column(sa.Column('method_type', sa.String(20), nullable=False))
        batch_op.add_column(sa.Column('provider', sa.String(50), nullable=False))
        batch_op.add_column(sa.Column('provider_message_id', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('metadata', sa.JSON, nullable=True))
        
        # Add indexes
        batch_op.create_index('idx_user_method', ['user_id', 'method_type'])
        batch_op.create_index('idx_status', ['status', 'created_at'])
        batch_op.create_index('idx_provider', ['provider', 'created_at'])

    # Update user_verification_methods table
    with op.batch_alter_table('user_verification_methods') as batch_op:
        # Add new columns
        batch_op.add_column(sa.Column('identifier', sa.String(120), nullable=False))
        batch_op.add_column(sa.Column('verification_token', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('token_expires', sa.DateTime, nullable=True))
        batch_op.add_column(sa.Column('verified_at', sa.DateTime, nullable=True))
        batch_op.add_column(sa.Column('last_verification_attempt', sa.DateTime, nullable=True))
        batch_op.add_column(sa.Column('verification_attempts', sa.Integer, nullable=False, server_default='0'))
        
        # Add indexes
        batch_op.create_index('idx_identifier', ['method_type', 'identifier'])
        batch_op.create_index('idx_token', ['verification_token'])

def downgrade():
    # Remove added columns and indexes from customers table
    with op.batch_alter_table('customers') as batch_op:
        batch_op.drop_index('idx_customer_assignment')
        batch_op.drop_index('idx_customer_email')
        batch_op.drop_index('idx_customer_phone')
        batch_op.drop_index('idx_customer_business')
        batch_op.drop_index('idx_last_activity')
        batch_op.drop_index('idx_search')
        batch_op.drop_column('nickname')
        batch_op.drop_column('business_name')
        batch_op.drop_column('city')
        batch_op.drop_column('state')
        batch_op.drop_column('zip_code')
        batch_op.drop_column('country')
        batch_op.drop_column('metadata')
        batch_op.drop_column('last_activity_at')
        batch_op.drop_column('shipping_address')
        batch_op.drop_column('search_vector')
        batch_op.alter_column('assigned_at', new_column_name='last_assigned_at')

    # Remove added columns and indexes from user_profiles table
    with op.batch_alter_table('user_profiles') as batch_op:
        batch_op.drop_index('idx_business')
        batch_op.drop_index('idx_phone')
        batch_op.drop_index('idx_search')
        batch_op.drop_column('first_name')
        batch_op.drop_column('last_name')
        batch_op.drop_column('business_name')
        batch_op.drop_column('street')
        batch_op.drop_column('city')
        batch_op.drop_column('state')
        batch_op.drop_column('zip_code')
        batch_op.drop_column('country')
        batch_op.drop_column('phone_number')
        batch_op.drop_column('tin_trunk_phone')
        batch_op.drop_column('metadata')
        batch_op.drop_column('search_vector')

    # Remove added columns and indexes from activity_logs table
    with op.batch_alter_table('activity_logs') as batch_op:
        batch_op.drop_index('idx_user_action')
        batch_op.drop_index('idx_entity')
        batch_op.drop_index('idx_created_at')
        batch_op.alter_column('action_type', new_column_name='activity_type')
        batch_op.drop_column('entity_type')
        batch_op.drop_column('entity_id')
        batch_op.drop_column('metadata')

    # Remove added columns and indexes from verification_messages_log table
    with op.batch_alter_table('verification_messages_log') as batch_op:
        batch_op.drop_index('idx_user_method')
        batch_op.drop_index('idx_status')
        batch_op.drop_index('idx_provider')
        batch_op.alter_column('identifier', new_column_name='sent_to')
        batch_op.drop_column('method_type')
        batch_op.drop_column('provider')
        batch_op.drop_column('provider_message_id')
        batch_op.drop_column('metadata')

    # Remove added columns and indexes from user_verification_methods table
    with op.batch_alter_table('user_verification_methods') as batch_op:
        batch_op.drop_index('idx_identifier')
        batch_op.drop_index('idx_token')
        batch_op.drop_column('identifier')
        batch_op.drop_column('verification_token')
        batch_op.drop_column('token_expires')
        batch_op.drop_column('verified_at')
        batch_op.drop_column('last_verification_attempt')
        batch_op.drop_column('verification_attempts') 