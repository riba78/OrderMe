"""
JSON Encoder Tests

Tests for the EnumEncoder class and related utility functions.
These tests verify that:
1. Enum values are properly serialized to JSON
2. Datetime and UUID objects are properly serialized
3. Custom type handlers can be registered
4. Enum values can be deserialized back to enum objects
5. Decimal values are properly serialized
"""

import json
import enum
import pytest
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal

from app.utils.json_encoder import EnumEncoder, serialize_enum, deserialize_enum
from app.models.enums import OrderStatus, UserRole, PaymentStatus, NotificationType

class TestEnumEncoder:
    def test_enum_serialization(self):
        """Test that enum values are properly serialized."""
        # Create a dictionary with enum values
        data = {
            "order_status": OrderStatus.PENDING,
            "payment_status": PaymentStatus.COMPLETED,
            "notification_type": NotificationType.PAYMENT
        }
        
        # Serialize to JSON
        json_str = serialize_enum(data)
        
        # Parse the JSON string back to a dictionary
        deserialized = json.loads(json_str)
        
        # Verify enum values are serialized as their string values
        assert deserialized["order_status"] == "pending"
        assert deserialized["payment_status"] == "completed"
        assert deserialized["notification_type"] == "payment"
    
    def test_datetime_serialization(self):
        """Test that datetime objects are properly serialized."""
        # Create a dictionary with datetime values
        now = datetime.now()
        today = date.today()
        data = {
            "timestamp": now,
            "date": today
        }
        
        # Serialize to JSON
        json_str = serialize_enum(data)
        
        # Parse the JSON string back to a dictionary
        deserialized = json.loads(json_str)
        
        # Verify datetime values are serialized as ISO format strings
        assert deserialized["timestamp"] == now.isoformat()
        assert deserialized["date"] == today.isoformat()
    
    def test_uuid_serialization(self):
        """Test that UUID objects are properly serialized."""
        # Create a dictionary with UUID values
        uuid = UUID('123e4567-e89b-12d3-a456-426614174000')
        data = {
            "id": uuid
        }
        
        # Serialize to JSON
        json_str = serialize_enum(data)
        
        # Parse the JSON string back to a dictionary
        deserialized = json.loads(json_str)
        
        # Verify UUID values are serialized as strings
        assert deserialized["id"] == str(uuid)
    
    def test_decimal_serialization(self):
        """Test that Decimal objects are properly serialized."""
        # Create a dictionary with Decimal values matching DECIMAL(10,2) precision
        price = Decimal('99.99')
        total = Decimal('1234567.89')  # Max value for DECIMAL(10,2)
        data = {
            "price": price,
            "total": total
        }
        
        # Serialize to JSON
        json_str = serialize_enum(data)
        
        # Parse the JSON string back to a dictionary
        deserialized = json.loads(json_str)
        
        # Verify Decimal values are serialized as floats
        assert deserialized["price"] == float(price)
        assert deserialized["total"] == float(total)
        assert isinstance(deserialized["price"], float)
        assert isinstance(deserialized["total"], float)
    
    def test_custom_type_handler(self):
        """Test that custom type handlers can be registered."""
        # Create a custom class
        class CustomClass:
            def __init__(self, value):
                self.value = value
        
        # Create a custom class instance
        custom_obj = CustomClass("test")
        
        # Create a custom encoder with a handler for CustomClass
        encoder = EnumEncoder()
        encoder.register_handler(CustomClass, lambda obj: obj.value)
        
        # Directly test the default method of the encoder
        result = encoder.default(custom_obj)
        
        # Verify the handler was used
        assert result == "test"
    
    def test_complex_structure_serialization(self):
        """Test serialization of complex nested structures with enums."""
        # Create a complex nested structure
        data = {
            "user": {
                "id": UUID('123e4567-e89b-12d3-a456-426614174000'),
                "role": UserRole.ADMIN
            },
            "orders": [
                {
                    "id": "1",
                    "status": OrderStatus.DELIVERED,
                    "items": [
                        {"product_id": "100", "quantity": 2, "price": Decimal('10.99')}
                    ],
                    "total": Decimal('21.98')
                },
                {
                    "id": "2",
                    "status": OrderStatus.PENDING,
                    "items": [
                        {"product_id": "200", "quantity": 1, "price": Decimal('99.99')}
                    ],
                    "total": Decimal('99.99')
                }
            ],
            "created_at": datetime(2023, 1, 1, 12, 0, 0)
        }
        
        # Serialize to JSON
        json_str = serialize_enum(data)
        
        # Parse the JSON string back to a dictionary
        deserialized = json.loads(json_str)
        
        # Verify the serialized structure
        assert deserialized["user"]["role"] == "admin"
        assert deserialized["orders"][0]["status"] == "delivered"
        assert deserialized["orders"][1]["status"] == "pending"
        assert deserialized["orders"][0]["total"] == float(Decimal('21.98'))
        assert deserialized["orders"][1]["total"] == float(Decimal('99.99'))
        assert deserialized["created_at"] == "2023-01-01T12:00:00"
    
    def test_enum_deserialization(self):
        """Test that enum values can be deserialized back to enum objects."""
        # Create a JSON string with enum values as strings
        json_str = '{"order_status": "pending", "user_role": "admin"}'
        
        # Define enum mapping
        enum_mapping = {
            "order_status": OrderStatus,
            "user_role": UserRole
        }
        
        # Deserialize with enum reconstruction
        deserialized = deserialize_enum(json_str, enum_mapping)
        
        # Verify enum values are reconstructed
        assert isinstance(deserialized["order_status"], OrderStatus)
        assert deserialized["order_status"] == OrderStatus.PENDING
        assert isinstance(deserialized["user_role"], UserRole)
        assert deserialized["user_role"] == UserRole.ADMIN
    
    def test_complex_enum_deserialization(self):
        """Test deserialization of complex nested structures with enums."""
        # Create a JSON string with nested structures containing enum values
        json_str = '''
        {
            "user": {
                "role": "admin"
            },
            "orders": [
                {
                    "id": "1",
                    "status": "delivered"
                },
                {
                    "id": "2",
                    "status": "pending"
                }
            ]
        }
        '''
        
        # Define enum mapping
        enum_mapping = {
            "role": UserRole,
            "status": OrderStatus
        }
        
        # Deserialize with enum reconstruction
        deserialized = deserialize_enum(json_str, enum_mapping)
        
        # Verify enum values are reconstructed in nested structures
        assert isinstance(deserialized["user"]["role"], UserRole)
        assert deserialized["user"]["role"] == UserRole.ADMIN
        
        assert isinstance(deserialized["orders"][0]["status"], OrderStatus)
        assert deserialized["orders"][0]["status"] == OrderStatus.DELIVERED
        
        assert isinstance(deserialized["orders"][1]["status"], OrderStatus)
        assert deserialized["orders"][1]["status"] == OrderStatus.PENDING 