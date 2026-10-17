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
import time
import threading
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, Request, Response, status
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

# Consistent persistent secret key prevents mass session invalidation on server restart
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "scrapsense-ai-production-super-secret-key-2026-v2")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24
SESSION_COOKIE_NAME = "scrapsense_session"

security = HTTPBearer(auto_error=False)


# ---------------- PASSWORD SECURITY & STRENGTH POLICY ----------------
COMMON_BREACHED_PASSWORDS = {
    "123456", "12345678", "123456789", "password", "password123", "password123!", "admin123",
    "admin@123", "admin@12345", "welcome@123", "p@ssword123", "p@ssw0rd123",
    "scrapsense", "scrapsense123", "scrapsense123!", "qwerty", "qwertyuiop", "welcome123",
    "iloveyou", "secret123", "letmein123", "monkey123", "dragon123",
    "testing123", "pass1234", "password@123"
}


def validate_password_strength(password: str) -> None:
    """Enforces strong password rules and blocks common breached passwords."""
    if not password or len(password) < 10:
        raise HTTPException(
            status_code=422,
            detail="Password must contain at least 10 characters."
        )
    if password.lower() in COMMON_BREACHED_PASSWORDS:
        raise HTTPException(
            status_code=422,
            detail="This password is too common or known to be compromised. Choose a stronger password."
        )
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in r"!@#$%^&*()_+-=[]{}|;:,.<>/?`~" for c in password)

    missing = []
    if not has_upper: missing.append("an uppercase letter (A-Z)")
    if not has_lower: missing.append("a lowercase letter (a-z)")
    if not has_digit: missing.append("a number (0-9)")
    if not has_special: missing.append("a special character (!@#$%^&*)")

    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Password must include {', '.join(missing)}."
        )
    return True


# ---------------- SLIDING WINDOW RATE LIMITER ----------------
class SlidingWindowRateLimiter:
    """In-memory rate limiter with temporary lockout for login & OTP brute-force defense."""
    def __init__(self):
        self._lock = threading.Lock()
        self._attempts: dict[str, list[float]] = {}
        self._lockouts: dict[str, float] = {}

    def check(self, key: str, max_attempts: int, window_seconds: int, lockout_seconds: int = 0) -> None:
        now = time.time()
        with self._lock:
            # Check if currently locked out
            locked_until = self._lockouts.get(key, 0.0)
            if now < locked_until:
                remaining = int(locked_until - now)
                raise HTTPException(
                    status_code=429,
                    detail=f"Too many failed attempts. Temporarily locked out. Please wait {remaining} seconds.",
                    headers={"Retry-After": str(remaining)}
                )

            # Clean expired attempts outside window
            timestamps = self._attempts.get(key, [])
            timestamps = [t for t in timestamps if now - t < window_seconds]
            self._attempts[key] = timestamps

            if len(timestamps) >= max_attempts:
                if lockout_seconds > 0:
                    self._lockouts[key] = now + lockout_seconds
                remaining = lockout_seconds or window_seconds
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded ({max_attempts} attempts reached). Temporarily locked out for {remaining} seconds.",
                    headers={"Retry-After": str(remaining)}
                )

    def record_attempt(self, key: str) -> None:
        now = time.time()
        with self._lock:
            timestamps = self._attempts.get(key, [])
            timestamps.append(now)
            self._attempts[key] = timestamps

    def reset(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)
            self._lockouts.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._attempts.clear()
            self._lockouts.clear()


rate_limiter = SlidingWindowRateLimiter()


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


def set_auth_cookie(response: Response, token: str) -> None:
    """Sets secure httpOnly cookie for session token protection against XSS."""
    # 24 hours max age
    max_age = TOKEN_EXPIRE_HOURS * 3600
    is_prod = os.getenv("ENVIRONMENT", "development").lower() == "production"
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=max_age,
        expires=max_age,
        httponly=True,
        samesite="lax",
        secure=is_prod,
        path="/"
    )


def clear_auth_cookie(response: Response) -> None:
    """Deletes the session cookie on logout."""
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        samesite="lax"
    )


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    FastAPI dependency: extracts and verifies JWT.
    Checks httpOnly session cookie first, falling back to Authorization header.
    """
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token and credentials is not None:
        token = credentials.credentials

    if not token:
        raise HTTPException(status_code=401, detail="Authentication required. Please login.")

    payload = decode_token(token)
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
