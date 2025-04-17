"""
JSON Encoder Module

This module provides JSON encoding utilities for the application,
particularly for handling special data types like enums that are
not natively serializable in JSON.
"""

import json
import enum
from datetime import datetime, date
from uuid import UUID
from typing import Any, Optional, Dict, List, Union, Callable
from decimal import Decimal

class EnumEncoder(json.JSONEncoder):
    """
    JSON encoder that properly serializes enum values and other special types.
    
    Follows the Single Responsibility Principle by focusing only on serialization.
    Follows the Open/Closed Principle by allowing extension for new types without 
    modifying existing code through the type_handlers mechanism.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the encoder with default type handlers."""
        super().__init__(*args, **kwargs)
        # Define handlers for each special type - extensible for new types
        self.type_handlers = {
            enum.Enum: lambda obj: obj.value,
            datetime: lambda obj: obj.isoformat(),
            date: lambda obj: obj.isoformat(),
            UUID: lambda obj: str(obj),
            Decimal: lambda obj: float(obj)  # Convert Decimal to float for JSON serialization
        }
    
    def register_handler(self, type_class: type, handler: Callable[[Any], Any]) -> None:
        """
        Register a new type handler to extend serialization capabilities.
        
        Args:
            type_class: The class type to handle
            handler: A callable that converts the object to a JSON-serializable type
        """
        self.type_handlers[type_class] = handler
    
    def default(self, obj: Any) -> Any:
        """
        Convert objects to JSON-serializable types.
        
        Args:
            obj: The object to serialize
            
        Returns:
            A JSON-serializable representation of the object
            
        Raises:
            TypeError: If the object cannot be serialized
        """
        # Try each registered handler
        for cls, handler in self.type_handlers.items():
            if isinstance(obj, cls):
                return handler(obj)
        
        # Fallback to default serialization
        return super().default(obj)

def serialize_enum(obj: Any) -> str:
    """
    Serialize an object with enum values to a JSON string.
    
    Args:
        obj: The object to serialize
        
    Returns:
        A JSON string representation of the object
    """
    return json.dumps(obj, cls=EnumEncoder)

def deserialize_enum(json_str: str, enum_mapping: Optional[Dict[str, enum.Enum]] = None) -> Any:
    """
    Deserialize a JSON string, with optional enum reconstruction.
    
    Args:
        json_str: The JSON string to deserialize
        enum_mapping: Optional dictionary mapping field names to enum types
        
    Returns:
        The deserialized object with enum values converted back to enum objects
        if enum_mapping is provided
    """
    data = json.loads(json_str)
    
    if enum_mapping:
        _reconstruct_enums(data, enum_mapping)
    
    return data

def _reconstruct_enums(data: Any, enum_mapping: Dict[str, enum.Enum]) -> None:
    """
    Recursively reconstruct enum values in deserialized data.
    
    Args:
        data: The data structure to process
        enum_mapping: Dictionary mapping field names to enum types
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key in enum_mapping and value is not None:
                data[key] = enum_mapping[key](value)
            elif isinstance(value, (dict, list)):
                _reconstruct_enums(value, enum_mapping)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                _reconstruct_enums(item, enum_mapping) 