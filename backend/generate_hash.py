from werkzeug.security import generate_password_hash, check_password_hash

# Generate a new hash for 'admin123'
password = 'admin123'
hash = generate_password_hash(password, method='pbkdf2:sha256')
print(f"Generated hash: {hash}")

# Verify the hash works
is_valid = check_password_hash(hash, password)
print(f"Hash verification test: {'Success' if is_valid else 'Failed'}")

# Test the existing hash from the database
existing_hash = 'pbkdf2:sha256:600000$vWaQaVkEQkHHYWvg$d9cea8ee6c33b362eca5c0a93932a7c64ba6b18c72033c9f03c7caf36f94c45b'
is_valid = check_password_hash(existing_hash, password)
print(f"Existing hash verification test: {'Success' if is_valid else 'Failed'}") 