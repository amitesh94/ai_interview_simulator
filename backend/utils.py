import bcrypt

def hash_password(password: str) -> str:
    """Hash password using bcrypt directly."""
    # Encode to bytes and truncate to 72 bytes (bcrypt limit)
    password_bytes = password.encode("utf-8")[:72]
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt directly."""
    # Encode to bytes and truncate to 72 bytes (bcrypt limit)
    password_bytes = plain_password.encode("utf-8")[:72]
    # Compare with stored hash
    return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))

