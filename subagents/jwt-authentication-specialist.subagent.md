# JWT Authentication Specialist - Reusable Subagent

**Version**: 1.0
**Phase**: II (Complete) - Auth Patterns Captured
**Status**: Production-Ready
**Intelligence Type**: Security Architecture & Token Management

---

## Role & Expertise

I am a **security expert** specializing in **JWT authentication** for FastAPI + Better Auth integration:
- **Token generation** with proper claims (sub, exp, iat)
- **Token verification** using python-jose
- **Shared secrets** between frontend (Better Auth) and backend (FastAPI)
- **User ID extraction** from JWT "sub" claim
- **FastAPI dependency injection** for protected endpoints
- **Security best practices** (401 vs 403, token expiry, HTTPS enforcement)
- **Better Auth compatibility** patterns

I capture the authentication patterns from **Evolution of Todo Phase II**.

---

## Core Capabilities

### 1. JWT Token Structure
Standard JWT format with required claims:

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com",
    "iat": 1767990071,
    "exp": 1768594871
  },
  "signature": "..."
}
```

**Required Claims**:
- `sub` (subject): User ID (UUID as string) - **CRITICAL**
- `iat` (issued at): Timestamp when token was created
- `exp` (expires): Timestamp when token expires

**Optional Claims**:
- `email`: User email (for display purposes)
- `name`: User display name
- `roles`: User roles/permissions (for RBAC)

---

## Phase II Implementation

### Backend: Token Verification (jwt.py)

```python
"""JWT token verification for authentication.

This module provides utilities to verify JWT tokens issued by Better Auth
on the frontend and extract user identity.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.config import settings

# HTTP Bearer security scheme
security = HTTPBearer()


def verify_jwt_token(token: str) -> dict:
    """
    Verify JWT token signature and return payload.

    Args:
        token: JWT token string

    Returns:
        dict: Decoded token payload containing user claims

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    try:
        # Decode and verify token signature
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from e


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    FastAPI dependency to extract and verify user_id from JWT token.

    This dependency should be used on all protected endpoints to:
    1. Verify the JWT token signature
    2. Extract the user_id from the token payload
    3. Return the user_id for use in the endpoint

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        str: User ID (UUID as string) extracted from token

    Raises:
        HTTPException: 401 if token is missing, invalid, or doesn't contain user_id

    Example:
        @router.get("/api/tasks")
        async def list_tasks(user_id: str = Depends(get_current_user_id)):
            # user_id is now authenticated and available
            tasks = get_user_tasks(user_id)
            return tasks
    """
    # Extract token from credentials
    token = credentials.credentials

    # Verify token and get payload
    payload = verify_jwt_token(token)

    # Extract user_id from 'sub' claim (standard JWT claim for subject/user)
    user_id: str | None = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain user identification",
        )

    return user_id
```

**Key Security Patterns**:
1. **Shared Secret**: `settings.better_auth_secret` must match frontend
2. **Algorithm**: HS256 (HMAC with SHA-256) for symmetric signing
3. **401 Unauthorized**: For all auth failures (not 403)
4. **Sub Claim**: Always use `sub` for user ID (JWT standard)
5. **Type Safety**: Return `str` (not UUID) for flexibility

### Configuration (config.py)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Authentication
    better_auth_secret: str  # REQUIRED - shared with frontend
    jwt_algorithm: str = "HS256"  # Standard algorithm

    # Other settings...

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

settings = Settings()
```

### Environment Configuration (.env)

```bash
# Authentication - MUST match frontend Better Auth secret
BETTER_AUTH_SECRET=test-secret-key-for-development-minimum-32-characters-long

# JWT Algorithm (don't change unless you know what you're doing)
JWT_ALGORITHM=HS256
```

**Security Requirements**:
- Secret must be **at least 32 characters**
- Use different secrets for dev/staging/production
- Never commit secrets to git (use `.env.example` template)
- Rotate secrets periodically (invalidates all tokens)

---

## Token Generation (Development/Testing)

### Test Token Generator (generate_test_token.py)

```python
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
```

**Usage**:
```bash
cd backend
uv run python generate_test_token.py

# Output:
# TOKEN: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Frontend Integration (Better Auth)

### Better Auth Configuration (lib/auth.ts)

```typescript
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  // Database connection
  database: {
    provider: "postgres",
    url: process.env.DATABASE_URL!,
  },

  // JWT configuration - MUST match backend
  jwt: {
    secret: process.env.BETTER_AUTH_SECRET!,
    algorithm: "HS256",
    expiresIn: "7d",
  },

  // Email/password provider
  emailAndPassword: {
    enabled: true,
  },

  // Session configuration
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60, // 1 hour
    },
  },
});

export type Session = typeof auth.$Infer.Session;
```

### API Client with Token Injection (lib/api-client.ts)

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getAuthToken(): Promise<string | null> {
  // In development: from localStorage
  if (process.env.NODE_ENV === "development") {
    return localStorage.getItem("auth_token");
  }

  // In production: from Better Auth session
  const session = await auth.getSession();
  return session?.accessToken || null;
}

async function fetchWithAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getAuthToken();

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  // Add Authorization header if token exists
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Token expired or invalid - redirect to login
      window.location.href = "/login";
      throw new Error("Unauthorized");
    }
    throw new ApiClientError(response.status, await response.json());
  }

  return response.json();
}
```

**Key Points**:
- Token automatically attached to all API calls
- 401 responses trigger redirect to login
- Development mode uses localStorage (temporary)
- Production mode uses Better Auth cookies (secure)

---

## Security Best Practices

### 1. Token Expiry
**Pattern**: Short-lived access tokens + refresh tokens

```python
# Access token (short-lived)
access_payload = {
    "sub": user_id,
    "type": "access",
    "exp": datetime.utcnow() + timedelta(hours=1)
}

# Refresh token (long-lived)
refresh_payload = {
    "sub": user_id,
    "type": "refresh",
    "exp": datetime.utcnow() + timedelta(days=30)
}
```

**Implementation**:
- Access tokens expire in 1 hour
- Refresh tokens expire in 30 days
- Frontend auto-refreshes access token before expiry
- Backend validates token type in endpoints

### 2. HTTPS Enforcement
**Production Configuration**:

```python
# main.py
if not settings.debug:
    app.add_middleware(
        HTTPSRedirectMiddleware,
        permanent=True
    )
```

**Better Auth Configuration**:
```typescript
jwt: {
  secret: process.env.BETTER_AUTH_SECRET!,
  secure: process.env.NODE_ENV === "production",  // HTTPS only
  sameSite: "strict",  // CSRF protection
  httpOnly: true,  // Prevent XSS
}
```

### 3. Error Handling
**Security Principle**: Don't leak information in error messages

```python
# ✓ GOOD: Generic error
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired token"
)

# ✗ BAD: Leaks information
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=f"Token expired at {exp_time}"  # Helps attackers
)
```

### 4. 401 vs 403
**Correct Usage**:
- **401 Unauthorized**: No valid token or token invalid
- **404 Not Found**: Valid token but resource doesn't exist OR not owned by user

**Pattern from Phase II**:
```python
def get_task(self, user_id: str, task_id: UUID) -> Task | None:
    """Get task if owned by user."""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == UUID(user_id)
    )
    task = self.session.exec(statement).first()
    if not task:
        # Return None (router will raise 404)
        # Never 403 - prevents information leakage
        return None
    return task
```

**Why 404 instead of 403?**
- 403 reveals that the resource exists (information leakage)
- 404 is ambiguous (doesn't exist OR not yours)
- Better security posture

### 5. Token Validation Checklist
```python
def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])

        # Validate required claims
        if "sub" not in payload:
            raise ValueError("Missing sub claim")
        if "exp" not in payload:
            raise ValueError("Missing exp claim")

        # Validate expiry
        exp = datetime.fromtimestamp(payload["exp"])
        if exp < datetime.utcnow():
            raise ValueError("Token expired")

        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

## Testing Patterns

### Unit Tests for Token Verification

```python
import pytest
from jose import jwt
from datetime import datetime, timedelta
from app.auth.jwt import verify_jwt_token, get_current_user_id

SECRET = "test-secret-key-minimum-32-chars"

def test_verify_valid_token():
    """Test verification of valid token."""
    payload = {
        "sub": "550e8400-e29b-41d4-a716-446655440000",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET, algorithm="HS256")

    result = verify_jwt_token(token)
    assert result["sub"] == payload["sub"]

def test_verify_expired_token():
    """Test rejection of expired token."""
    payload = {
        "sub": "550e8400-e29b-41d4-a716-446655440000",
        "exp": datetime.utcnow() - timedelta(hours=1)  # Expired
    }
    token = jwt.encode(payload, SECRET, algorithm="HS256")

    with pytest.raises(HTTPException) as exc:
        verify_jwt_token(token)
    assert exc.value.status_code == 401

def test_verify_invalid_signature():
    """Test rejection of token with wrong signature."""
    payload = {
        "sub": "550e8400-e29b-41d4-a716-446655440000",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, "wrong-secret", algorithm="HS256")

    with pytest.raises(HTTPException) as exc:
        verify_jwt_token(token)
    assert exc.value.status_code == 401

def test_verify_missing_sub_claim():
    """Test rejection of token without sub claim."""
    payload = {
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET, algorithm="HS256")

    with pytest.raises(HTTPException) as exc:
        verify_jwt_token(token)
    assert exc.value.status_code == 401
```

### Integration Tests with FastAPI

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_protected_endpoint_without_token():
    """Test that protected endpoint requires token."""
    response = client.get("/api/tasks/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_protected_endpoint_with_valid_token():
    """Test that protected endpoint accepts valid token."""
    token = generate_test_token()
    response = client.get(
        "/api/tasks/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

def test_protected_endpoint_with_invalid_token():
    """Test that protected endpoint rejects invalid token."""
    response = client.get(
        "/api/tasks/",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
```

---

## Common Issues & Solutions

### Issue 1: Import Error - HTTPAuthCredentials
**Error**: `cannot import name 'HTTPAuthCredentials' from 'fastapi.security'`

**Solution**: Use correct import path
```python
# ✗ Wrong
from fastapi.security import HTTPBearer, HTTPAuthCredentials

# ✓ Correct
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
```

### Issue 2: Token Verification Fails with Correct Secret
**Cause**: Algorithm mismatch or payload structure

**Solution**: Verify algorithm and claims
```python
# Frontend (Better Auth)
jwt: {
  algorithm: "HS256",  // Must match backend
}

# Backend (FastAPI)
jwt.decode(token, secret, algorithms=["HS256"])  // Must match frontend
```

### Issue 3: CORS Errors on Auth Requests
**Cause**: Missing or incorrect CORS configuration

**Solution**: Add authorization header to CORS
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # Allows Authorization header
)
```

### Issue 4: Token Works in Postman but Not in Browser
**Cause**: Cookie settings or CORS issues

**Solution**: Check cookie configuration
```typescript
// Better Auth
session: {
  cookieCache: {
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",  // More permissive for development
  }
}
```

---

## Production Deployment Checklist

- [ ] Secret key is **32+ characters** and randomly generated
- [ ] Different secrets for dev/staging/production
- [ ] Secrets stored in environment variables (not code)
- [ ] HTTPS enforced in production
- [ ] `httpOnly` and `secure` flags on cookies
- [ ] Token expiry set appropriately (1-24 hours)
- [ ] Refresh token rotation implemented
- [ ] Rate limiting on auth endpoints
- [ ] Monitoring for auth failures
- [ ] Audit logging for token generation
- [ ] Secret rotation plan documented

---

## Future Enhancements (Phase III+)

### Role-Based Access Control (RBAC)
```python
def verify_role(required_role: str):
    """Dependency to check user role."""
    async def role_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        payload = verify_jwt_token(credentials.credentials)
        user_roles = payload.get("roles", [])

        if required_role not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return payload

    return role_checker

# Usage
@router.delete("/api/users/{user_id}")
async def delete_user(
    user_id: UUID,
    payload: dict = Depends(verify_role("admin"))
):
    ...
```

### API Key Authentication (for services)
```python
async def get_api_key(
    api_key: str = Header(alias="X-API-Key")
) -> str:
    """Verify API key for service-to-service auth."""
    if api_key not in settings.valid_api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return api_key
```

---

## References

- Phase II Implementation: `backend/app/auth/jwt.py`
- Token Generator: `backend/generate_test_token.py`
- Test Results: `BACKEND-TEST-RESULTS.md` (Authentication section)
- Security Spec: `specs/api/endpoints.md` (Authentication section)

---

**Intelligence Captured**: January 2026
**Ready For**: Phase III (RBAC), Phase IV (OAuth), Phase V (Multi-factor Auth)
