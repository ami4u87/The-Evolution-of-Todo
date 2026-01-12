"""
Generate JWT token with proper UUID for user_id.
Invoked by JWT Authentication Specialist Subagent.
"""

from jose import jwt
from datetime import datetime, timedelta
import uuid

# Configuration from backend/.env
SECRET_KEY = "test-secret-key-for-development-minimum-32-characters-long"
ALGORITHM = "HS256"

# Generate a valid UUID for test user
test_user_uuid = str(uuid.uuid4())

# Create payload with required claims
payload = {
    "sub": test_user_uuid,  # Subject (user identifier) - MUST be UUID
    "email": "test-user@example.com",
    "iat": datetime.utcnow(),
    "exp": datetime.utcnow() + timedelta(days=7)
}

# Generate JWT token
token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Output
print("=" * 80)
print("JWT AUTHENTICATION SPECIALIST - CORRECTED TOKEN")
print("=" * 80)
print()
print("ISSUE FOUND: Backend expects UUID format for user_id")
print("SOLUTION: Generated proper UUID for test user")
print()
print("TOKEN CLAIMS:")
print(f"  sub (User ID - UUID): {payload['sub']}")
print(f"  email: {payload['email']}")
print(f"  iat (Issued At): {payload['iat']}")
print(f"  exp (Expires): {payload['exp']}")
print()
print("=" * 80)
print("FULL TOKEN STRING:")
print("=" * 80)
print()
print(token)
print()
print("=" * 80)
print("USAGE:")
print("=" * 80)
print()
print(f'curl -H "Authorization: Bearer {token}" \\')
print('     http://localhost:8000/api/tasks/')
print()
