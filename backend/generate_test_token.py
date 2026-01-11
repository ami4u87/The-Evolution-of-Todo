"""
Generate a test JWT token for development/testing.
This token can be used to authenticate API requests.
"""

from jose import jwt
from datetime import datetime, timedelta
import uuid

# Same secret as in .env
SECRET_KEY = "test-secret-key-for-development-minimum-32-characters-long"
ALGORITHM = "HS256"

# Create test user payload
payload = {
    "sub": "550e8400-e29b-41d4-a716-446655440000",  # Test user UUID
    "email": "test@example.com",
    "iat": datetime.utcnow(),
    "exp": datetime.utcnow() + timedelta(days=7)  # Valid for 7 days
}

# Generate token
token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

print("=" * 80)
print("TEST JWT TOKEN GENERATED")
print("=" * 80)
print()
print("User ID:", payload["sub"])
print("Email:", payload["email"])
print("Expires:", payload["exp"])
print()
print("TOKEN:")
print(token)
print()
print("=" * 80)
print("USAGE:")
print("=" * 80)
print()
print("Export as environment variable:")
print(f'export TOKEN="{token}"')
print()
print("Or use in curl:")
print(f'curl -H "Authorization: Bearer {token}" http://localhost:8000/api/tasks')
print()
print("Or paste in login page at http://localhost:3000/login")
print()
