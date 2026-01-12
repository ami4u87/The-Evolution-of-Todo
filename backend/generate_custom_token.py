"""
Generate a custom JWT token for manual testing.
Invoked by JWT Authentication Specialist Subagent.
"""

from jose import jwt
from datetime import datetime, timedelta

# Configuration from backend/.env
SECRET_KEY = "test-secret-key-for-development-minimum-32-characters-long"
ALGORITHM = "HS256"

# Custom user ID as requested
USER_ID = "test-user-123"

# Create payload with required claims
payload = {
    "sub": USER_ID,  # Subject (user identifier) - REQUIRED
    "email": "test-user-123@example.com",  # Optional: for display
    "iat": datetime.utcnow(),  # Issued at timestamp
    "exp": datetime.utcnow() + timedelta(days=7)  # Expires in 7 days
}

# Generate JWT token
token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Output token details
print("=" * 80)
print("JWT AUTHENTICATION SPECIALIST - TOKEN GENERATOR")
print("=" * 80)
print()
print("CONFIGURATION:")
print(f"  Secret: {SECRET_KEY[:20]}...")
print(f"  Algorithm: {ALGORITHM}")
print()
print("TOKEN CLAIMS:")
print(f"  sub (User ID): {payload['sub']}")
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
print("USAGE EXAMPLES:")
print("=" * 80)
print()
print("1. Export as environment variable:")
print(f'   export TOKEN="{token}"')
print()
print("2. Use with curl:")
print(f'   curl -H "Authorization: Bearer {token}" \\')
print('        http://localhost:8000/api/tasks')
print()
print("3. Use in JavaScript fetch:")
print("   fetch('http://localhost:8000/api/tasks', {")
print("     headers: {")
print(f"       'Authorization': 'Bearer {token}'")
print("     }")
print("   })")
print()
print("4. Paste in frontend login page:")
print("   http://localhost:3000/login")
print(f"   Token: {token}")
print()
print("=" * 80)
print("VERIFICATION:")
print("=" * 80)
print()
print("To verify this token works:")
print("1. Start backend: cd backend && uvicorn app.main:app --reload")
print("2. Test endpoint:")
print(f'   curl -H "Authorization: Bearer {token}" \\')
print('        http://localhost:8000/api/tasks')
print()
print("Expected: 200 OK with empty task list []")
print()
