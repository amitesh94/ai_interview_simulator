from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    # Encode to bytes, truncate to 72 bytes (bcrypt limit), then hash
    password_bytes = password.encode("utf-8")[:72]
    password_str = password_bytes.decode("utf-8", errors="ignore")
    return pwd_context.hash(password_str)


def verify_password(plain_password: str, hashed_password: str):
    # Encode to bytes, truncate to 72 bytes (bcrypt limit)
    password_bytes = plain_password.encode("utf-8")[:72]
    password_str = password_bytes.decode("utf-8", errors="ignore")
    return pwd_context.verify(password_str, hashed_password)

