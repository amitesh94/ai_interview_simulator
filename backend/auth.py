from datetime import datetime, timedelta
import base64
import json
import hmac
import hashlib

SECRET_KEY = "af4b8a9c0f139e31c94efb8b05d8c6f2ad37b4e4d5c190a4859afde0b9a823ff"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ---------------------------------------------------------
# Helper: Base64 URL Encoding
# ---------------------------------------------------------
def _base64url_encode(input_bytes: bytes) -> str:
    return base64.urlsafe_b64encode(input_bytes).rstrip(b'=').decode('utf-8')

def _base64url_decode(input_str: str) -> bytes:
    padding = "=" * (-len(input_str) % 4)
    return base64.urlsafe_b64decode(input_str + padding)


# ---------------------------------------------------------
# JWT Encode
# ---------------------------------------------------------
def _jwt_encode(payload: dict, secret: str, algorithm: str = "HS256") -> str:
    header = {"alg": algorithm, "typ": "JWT"}

    header_b64 = _base64url_encode(json.dumps(header, separators=(',', ':')).encode())
    payload_b64 = _base64url_encode(json.dumps(payload, separators=(',', ':')).encode())

    signing_input = f"{header_b64}.{payload_b64}".encode()

    if algorithm == "HS256":
        signature = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    signature_b64 = _base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"


# ---------------------------------------------------------
# JWT Decode + Verify
# ---------------------------------------------------------
def verify_token(token: str):
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError:
        return None  # invalid format

    # Recreate signature
    signing_input = f"{header_b64}.{payload_b64}".encode()
    expected_sig = hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    expected_sig_b64 = _base64url_encode(expected_sig)

    # Signature mismatch
    if not hmac.compare_digest(signature_b64, expected_sig_b64):
        return None

    # Decode payload
    payload_json = _base64url_decode(payload_b64)
    payload = json.loads(payload_json)

    # Check expiration
    if "exp" in payload:
        if datetime.utcnow().timestamp() > payload["exp"]:
            return None  # token expired

    return payload  # valid JWT payload


# ---------------------------------------------------------
# Public Method: Create JWT Token
# ---------------------------------------------------------
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp())})
    return _jwt_encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
