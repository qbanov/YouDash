import re
import logging

logger = logging.getLogger(__name__)

def validate_serial_number(serial):
    if not serial:
        return False, "Serial number is required"
    
    if not isinstance(serial, (str, int)):
        return False, "Serial number must be a string or integer"
    
    serial_str = str(serial).strip()
    if not serial_str.isdigit():
        return False, "Serial number can only contain digits"
    
    return True, None

def validate_coordinates(x, y):
    try:
        x_float = float(x) if x is not None else None
        y_float = float(y) if y is not None else None
        
        if x_float is not None and (x_float < -180 or x_float > 180):
            return False, "X coordinate must be between -180 and 180"
        
        if y_float is not None and (y_float < -90 or y_float > 90):
            return False, "Y coordinate must be between -90 and 90"
        
        return True, None
    except (ValueError, TypeError):
        return False, "Coordinates must be valid numbers"

def validate_id(id_value, field_name="ID"):
    if not id_value:
        return False, f"{field_name} is required"
    
    try:
        id_int = int(id_value)
        if id_int <= 0:
            return False, f"{field_name} must be a positive integer"
        return True, None
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid integer"

def validate_string_length(value, field_name, min_length=1, max_length=255):
    if not value or not isinstance(value, str):
        return False, f"{field_name} must be a non-empty string"
    
    value = value.strip()
    if len(value) < min_length:
        return False, f"{field_name} must be at least {min_length} characters long"
    
    if len(value) > max_length:
        return False, f"{field_name} must be no more than {max_length} characters long"
    
    return True, None

def sanitize_input(value):
    if isinstance(value, str):
        return value.strip()
    return value
