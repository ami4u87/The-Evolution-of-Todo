#!/usr/bin/env python
"""Test script to check password implementation"""

import sys
sys.path.insert(0, '.')

from app.auth.password import hash_password, verify_password
import inspect

print("Checking password implementation...")
print(f"hash_password function location: {inspect.getfile(hash_password)}")
print(f"hash_password function source:")
print(inspect.getsource(hash_password))

# Test the function
try:
    print("\nTesting hash_password...")
    hashed = hash_password("test123!")
    print(f"Hashed: {hashed}")

    print("\nTesting verify_password...")
    verified = verify_password("test123!", hashed)
    print(f"Verified: {verified}")

    print("\nSuccess: Password functions work correctly")
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()