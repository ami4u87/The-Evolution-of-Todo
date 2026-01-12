"""
Generate multiple JWT tokens for testing different users.
JWT Authentication Specialist Subagent
"""

from jose import jwt
from datetime import datetime, timedelta
import uuid

# Configuration
SECRET_KEY = "test-secret-key-for-development-minimum-32-characters-long"
ALGORITHM = "HS256"

# Generate 3 different test users
test_users = [
    {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "user_id": str(uuid.uuid4())
    },
    {
        "name": "Bob Smith",
        "email": "bob@example.com",
        "user_id": str(uuid.uuid4())
    },
    {
        "name": "Charlie Brown",
        "email": "charlie@example.com",
        "user_id": str(uuid.uuid4())
    }
]

print("=" * 80)
print("JWT AUTHENTICATION SPECIALIST - MULTIPLE TEST TOKENS")
print("=" * 80)
print()

for i, user in enumerate(test_users, 1):
    # Create payload
    payload = {
        "sub": user["user_id"],
        "email": user["email"],
        "name": user["name"],
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=7)
    }

    # Generate token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    print(f"USER {i}: {user['name']}")
    print(f"Email: {user['email']}")
    print(f"User ID: {user['user_id']}")
    print(f"Token:")
    print(token)
    print()
    print(f"Set in Console:")
    print(f"localStorage.setItem('auth_token', '{token}');")
    print()
    print("-" * 80)
    print()
