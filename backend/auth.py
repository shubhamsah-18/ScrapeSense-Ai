"""
ScrapSense AI - Authentication & Authorization Module
---
Resilient JWT Authentication with Built-in Fallback:
1. On login, generate JWT token with payload {sub: email, role: role, name: name, exp: now+24h}
2. Sign token using HS256 with SECRET_KEY
3. On protected routes, decode & verify token from Authorization: Bearer header
4. Extract user info from verified token claims
5. Check role permissions for endpoint access
"""
import os
import json
import base64
import hmac
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

try:
    import jwt
    HAS_JWT = True
except ImportError:
    HAS_JWT = False

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False

SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Hash password using bcrypt or PBKDF2-HMAC fallback."""
    if HAS_BCRYPT:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()
    return f"pbkdf2:{salt}:{digest}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    if not hashed:
        return False
    if hashed.startswith("pbkdf2:"):
        try:
            parts = hashed.split(":")
            if len(parts) == 3:
                _, salt, digest = parts
                test_digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()
                return hmac.compare_digest(digest, test_digest)
        except Exception:
            return False
    if HAS_BCRYPT:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    return False


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip("=")


def _b64url_decode(data: str) -> bytes:
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data.encode('utf-8'))


def create_access_token(data: dict) -> str:
    """Generate signed JWT token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": int(expire.timestamp()), "iat": int(datetime.now(timezone.utc).timestamp())})

    if HAS_JWT:
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _b64url_encode(json.dumps(header).encode('utf-8'))
    payload_b64 = _b64url_encode(json.dumps(to_encode).encode('utf-8'))
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    sig = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(sig)
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_token(token: str) -> dict:
    """Decode and verify JWT token. Returns payload dict or raises HTTPException."""
    if HAS_JWT:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired. Please login again.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid authentication token.")

    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise HTTPException(status_code=401, detail="Invalid authentication token format.")
        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
        actual_sig = _b64url_decode(sig_b64)
        if not hmac.compare_digest(expected_sig, actual_sig):
            raise HTTPException(status_code=401, detail="Invalid token signature.")

        payload = json.loads(_b64url_decode(payload_b64).decode('utf-8'))
        exp = payload.get("exp")
        if exp and datetime.now(timezone.utc).timestamp() > exp:
            raise HTTPException(status_code=401, detail="Token has expired. Please login again.")
        return payload
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication token.")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """FastAPI dependency: extracts and verifies JWT from Authorization header."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required. Please login.")
    payload = decode_token(credentials.credentials)
    email = payload.get("sub")
    role = payload.get("role")
    name = payload.get("name", "User")
    if not email or not role:
        raise HTTPException(status_code=401, detail="Invalid token payload.")
    return {"email": email, "role": role, "name": name}


def require_role(*allowed_roles):
    """Role-Based Access Control (RBAC) dependency."""
    async def role_checker(user: dict = Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}"
            )
        return user
    return role_checker
