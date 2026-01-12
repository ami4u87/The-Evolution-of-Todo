"""
Password hashing utilities for authentication.

Migrated from Phase I security patterns with the following changes:
- Added SHA-256 password hashing with salt (temporary until bcrypt issue resolved)
- Implemented password verification
- Maintained same interface for consistency
"""

import hashlib
import secrets


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256 with random salt.

    Args:
        password: Plain text password to hash

    Returns:
        str: Hashed password string (format: salt:hashed_password)
    """
    # Generate a random salt
    salt = secrets.token_hex(16)
    # Combine password and salt, then hash
    pwdhash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    # Return salt and hash combined
    return f"{salt}:{pwdhash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Previously hashed password to compare against

    Returns:
        bool: True if password matches, False otherwise
    """
    # Split the stored hash to get salt and hash
    salt, stored_hash = hashed_password.split(':')
    # Hash the provided password with the stored salt
    pwdhash = hashlib.sha256((plain_password + salt).encode('utf-8')).hexdigest()
    # Compare the hashes
    return pwdhash == stored_hash