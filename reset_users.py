"""
ScrapSense AI - Registered Users Reset Tool
===========================================
Resets all registered users in MongoDB back to clean default demonstration accounts.
Removes test/dummy accounts, clears pending OTPs, and restores default logins.

Run via terminal:
    python reset_users.py
"""

import os
import sys
import hashlib
import secrets
from datetime import datetime, timezone
from pymongo import MongoClient

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
DB_NAME = os.getenv("MONGODB_DATABASE", "scrapsense")


def hash_pw(password: str):
    """PBKDF2-HMAC password hashing matching ScrapSense backend."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120000).hex()
    return salt, digest


DEFAULT_USERS = [
    # Administrator
    {
        "name": "System Administrator",
        "email": "7488114039",
        "role": "admin",
        "password": "password123",
        "phone": "+91 7488114039",
        "login_count": 42
    },
    {
        "name": "System Administrator",
        "email": "admin@scrapsense.org",
        "role": "admin",
        "password": "password123",
        "phone": "+91 7488114039",
        "login_count": 42
    },
    # Verified Sellers
    {
        "name": "Rajesh Sharma (Apex Metals)",
        "email": "apex.metals@scrapsense.org",
        "role": "seller",
        "password": "password123",
        "phone": "+91 98290 11223",
        "city": "Jaipur",
        "state": "Rajasthan",
        "login_count": 28
    },
    {
        "name": "Karthik Nair (Silicon City)",
        "email": "silicon.escrap@scrapsense.org",
        "role": "seller",
        "password": "password123",
        "phone": "+91 98451 88990",
        "city": "Bengaluru",
        "state": "Karnataka",
        "login_count": 19
    },
    {
        "name": "Pooja Patel (CleanPoly)",
        "email": "cleanpoly@scrapsense.org",
        "role": "seller",
        "password": "password123",
        "phone": "+91 98260 55443",
        "city": "Indore",
        "state": "Madhya Pradesh",
        "login_count": 14
    },
    {
        "name": "Amit Verma (GreenPower Battery)",
        "email": "greenpower@scrapsense.org",
        "role": "seller",
        "password": "password123",
        "phone": "+91 98101 22334",
        "city": "Delhi",
        "state": "Delhi",
        "login_count": 23
    },
    # Enterprise Buyers
    {
        "name": "Sunil Mehta - Tata Steel Circularity",
        "email": "procurement@tatasteel.com",
        "role": "buyer",
        "password": "password123",
        "phone": "+91 98220 99887",
        "city": "Mumbai",
        "state": "Maharashtra",
        "login_count": 31
    },
    {
        "name": "Vikram Singhania - Reliance Polymer Reclaim",
        "email": "buyer.polymers@ril.com",
        "role": "buyer",
        "password": "password123",
        "phone": "+91 98790 66778",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "login_count": 17
    },
    {
        "name": "Dr. Ananya Roy - EcoRecycle Smelters",
        "email": "purchase@ecorecycle.in",
        "role": "buyer",
        "password": "password123",
        "phone": "+91 98230 44332",
        "city": "Pune",
        "state": "Maharashtra",
        "login_count": 25
    }
]


def reset_all_registered_users(db=None):
    if db is None:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        db = client[DB_NAME]

    print("\n" + "=" * 70)
    print("  [+] SCRAPSENSE AI - RESETTING REGISTERED USERS")
    print("=" * 70)

    # 1. Inspect existing users
    old_count = db.users.count_documents({})
    print(f"[*] Found {old_count} existing user record(s) in 'users' collection.")

    # 2. Clear users collection
    del_res = db.users.delete_many({})
    print(f"[✓] Deleted {del_res.deleted_count} user record(s).")

    # 3. Clear pending OTP requests and password resets
    if "otp_requests" in db.list_collection_names():
        db.otp_requests.delete_many({})
        print("[✓] Cleared pending 'otp_requests' tokens.")
    if "password_resets" in db.list_collection_names():
        db.password_resets.delete_many({})
        print("[✓] Cleared pending 'password_resets' tokens.")

    # 4. Insert default accounts
    now = datetime.now(timezone.utc)
    inserted_users = []
    for u in DEFAULT_USERS:
        salt, pw_hash = hash_pw(u["password"])
        user_doc = {
            "name": u["name"],
            "email": u["email"].lower(),
            "role": u["role"],
            "salt": salt,
            "password_hash": pw_hash,
            "phone": u.get("phone", ""),
            "city": u.get("city", ""),
            "state": u.get("state", ""),
            "otp_verified": True,
            "login_count": u.get("login_count", 1),
            "created_at": now,
            "last_login": now
        }
        db.users.insert_one(user_doc)
        inserted_users.append(user_doc)

    print(f"[✓] Seeded {len(inserted_users)} authentic default accounts into 'users':")
    print("-" * 70)
    print(f"  {'ROLE':<8} | {'EMAIL / LOGIN ID':<30} | {'NAME / ORGANIZATION':<30}")
    print("-" * 70)
    for u in inserted_users:
        print(f"  [{u['role'].upper():<6}] | {u['email']:<30} | {u['name']:<30}")
    print("-" * 70)
    print("  Default password for all demo accounts: 'password123'")
    print("  Admin credentials: Login ID '7488114039' / Password 'password123'")
    print("=" * 70 + "\n")
    return len(inserted_users)


if __name__ == "__main__":
    try:
        reset_all_registered_users()
    except Exception as exc:
        print(f"[!] Error resetting users: {exc}")
        sys.exit(1)
