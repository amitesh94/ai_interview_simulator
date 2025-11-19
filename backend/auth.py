from datetime import datetime, timedelta
import base64
import json
import hmac
import hashlib

SECRET_KEY = "af4b8a9c0f139e31c94efb8b05d8c6f2ad37b4e4d5c190a4859afde0b9a823ff"  # change to strong key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def _base64url_encode(input_bytes: bytes) -> str:
    return base64.urlsafe_b64encode(input_bytes).rstrip(b'=').decode('utf-8')

def _jwt_encode(payload: dict, secret: str, algorithm: str = "HS256") -> str:
    header = {"alg": algorithm, "typ": "JWT"}
    header_b64 = _base64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    payload_b64 = _base64url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    if algorithm == "HS256":
        sig = hmac.new(secret.encode('utf-8'), signing_input, hashlib.sha256).digest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    signature_b64 = _base64url_encode(sig)
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp())})
    return _jwt_encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
