#!/usr/bin/env python
"""Debug script to check what happens when we import the auth modules"""

import sys
import os
sys.path.insert(0, os.getcwd())

print("=== Testing direct import ===")
from app.auth.password import hash_password, verify_password
print(f"Direct import - hash_password function: {hash_password}")
print(f"Direct import - function location: {hash_password.__module__}")

# Test the function directly
test_pass = "Test123!@"
hashed = hash_password(test_pass)
print(f"Direct hash result: {hashed[:20]}...")

print("\n=== Testing import through auth_service ===")
from app.services.auth_service import AuthService
print("AuthService imported successfully")

print("\n=== Testing import through auth router ===")
from app.routers import auth
print("Auth router imported successfully")

print("\n=== Testing if the issue occurs in isolation ===")
try:
    result = hash_password("debug_test_password")
    print(f"Isolated test passed: {result[:20]}...")
except Exception as e:
    print(f"Isolated test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== All imports successful ===")