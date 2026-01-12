#!/usr/bin/env python
"""Test to replicate the server environment"""

import sys
import os
sys.path.insert(0, os.getcwd())

# Simulate what happens in the auth_service
from sqlmodel import Session
from app.services.auth_service import AuthService
from app.schemas.auth import SignupRequest
from unittest.mock import MagicMock

print("=== Simulating auth service signup call ===")

# Mock a database session
mock_session = MagicMock(spec=Session)

# Create a test signup request
signup_data = SignupRequest(
    email="test@example.com",
    password="Test123!@",
    password_confirm="Test123!@"
)

# Create an auth service instance
auth_service = AuthService(mock_session)

try:
    print("Attempting to call auth_service.signup (which calls hash_password)...")
    # We'll catch the DB error since we're mocking, but the hash_password should work
    result = auth_service.signup(signup_data)
    print("Signup call succeeded")
except Exception as e:
    error_msg = str(e)
    print(f"Signup call resulted in error (expected due to mock): {error_msg}")

    # Check if it's the bcrypt error or just the DB error
    if "bcrypt" in error_msg or "hashpw" in error_msg:
        print("ERROR: The bcrypt error occurred during hash_password call!")
        import traceback
        traceback.print_exc()
    else:
        print("OK: The error is expected DB/mock error, not bcrypt error")

print("\n=== Test completed ===")