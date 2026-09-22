"""
ScrapSense AI - MongoDB Presentation & Inspection Tool
======================================================
Use this script to present and demonstrate your project database to your teacher/evaluator!

Run via terminal:
  python show_database.py
"""

import os
import sys

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from datetime import datetime
from pymongo import MongoClient

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
DB_NAME = os.getenv("MONGODB_DATABASE", "scrapsense")

def main():
    print("\n" + "=" * 78)
    print("  [+] SCRAPSENSE AI - MONGODB DATABASE PRESENTATION & INSPECTION REPORT")
    print("      Final Year Engineering Project · Live MongoDB Database System")
    print("=" * 78)

    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        db = client[DB_NAME]
    except Exception as exc:
        print(f"\n[!] Could not connect to MongoDB at {MONGODB_URI}: {exc}")
        print("Please make sure MongoDB Service is running (Windows Service or mongod).")
        sys.exit(1)

    print(f"\n[OK] MongoDB Connection : ACTIVE & RUNNING")
    print(f"[OK] Connection URI    : {MONGODB_URI}")
    print(f"[OK] Database Name     : {DB_NAME}")
    print(f"[OK] Current Time      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Summary table
    print("\n" + "-" * 78)
    print("  COLLECTIONS OVERVIEW (ALL DATA POPULATED IN DATABASE)")
    print("-" * 78)
    print(f"  {'Collection Name':<20} | {'Count':<10} | {'Description / College Project Value':<40}")
    print("  " + "-" * 74)

    descriptions = {
        "categories": "130 Authentic scrap materials across all 6 sectors",
        "listings": "30 Seller lots (24 verified + 6 pending approval)",
        "orders": "Transactions, Admin approvals & Buyer RFQs",
        "users": "Administrator, verified sellers & buyers",
        "dealers": "Verified Indian recycling dealer network",
        "analytics": "Platform circularity metrics & CO2 offset stats",
        "otp_requests": "OTP authentication security tokens"
    }

    total_docs = 0
    cols = sorted(db.list_collection_names())
    for col in cols:
        count = db[col].count_documents({})
        total_docs += count
        desc = descriptions.get(col, "System Data Collection")
        print(f"  * {col:<18} | {count:<10} | {desc:<40}")

    print("  " + "-" * 74)
    print(f"  TOTAL COLLECTIONS: {len(cols)} | TOTAL MONGODB DOCUMENTS: {total_docs}\n")

    # 1. Categories Breakdown
    if "categories" in cols:
        print("-" * 78)
        print("  1. CATEGORIES COLLECTION (130 ITEMS ACROSS 6 MATERIAL SECTORS)")
        print("-" * 78)
        from collections import Counter
        cat_counts = Counter(c.get("category", "Unknown") for c in db.categories.find())
        for cat, cnt in cat_counts.items():
            sample_items = [c.get("display_name") for c in db.categories.find({"category": cat}).limit(3)]
            print(f"  * {cat:<22} : {cnt:2} items -> e.g. {', '.join(sample_items)}")

    # 2. Listings Breakdown
    if "listings" in cols:
        print("\n" + "-" * 78)
        print("  2. MARKETPLACE LISTINGS COLLECTION (VERIFIED & PENDING LOTS)")
        print("-" * 78)
        verified_cnt = db.listings.count_documents({"verified": True})
        pending_cnt = db.listings.count_documents({"verified": False})
        print(f"  * Verified Lots for Buyers : {verified_cnt}")
        print(f"  * Pending Admin Approval   : {pending_cnt}")
        print("\n  Sample Marketplace Lots in Database:")
        for l in db.listings.find().limit(5):
            status = "[VERIFIED]" if l.get("verified") else "[PENDING ]"
            print(f"    {status} {l.get('item')} | Qty: {l.get('quantity')} {l.get('unit')} | Band: Rs.{l.get('min_price')}-Rs.{l.get('max_price')} | {l.get('city')}, {l.get('state')} | Seller: {l.get('seller')}")

    # 3. Orders Breakdown
    if "orders" in cols:
        print("\n" + "-" * 78)
        print("  3. ORDERS & TRANSACTIONS COLLECTION (APPROVAL WORKFLOW)")
        print("-" * 78)
        for o in db.orders.find().limit(5):
            st = o.get("status", "Pending")
            print(f"    * Lot: {o.get('lot')} | Qty: {o.get('quantity')} {o.get('unit')} | Offer: Rs.{o.get('offered_price')}/unit | Status: {st} | Buyer: {o.get('buyer_name', o.get('buyer'))}")

    # 4. Users Breakdown
    if "users" in cols:
        print("\n" + "-" * 78)
        print("  4. USERS COLLECTION (ROLE-BASED ACCESS CONTROL)")
        print("-" * 78)
        for u in db.users.find({}, {"password_hash": 0, "salt": 0}).limit(8):
            role_tag = f"[{u.get('role').upper()}]"
            print(f"    * {role_tag:<10} {u.get('name'):<32} | {u.get('email'):<30} | Logins: {u.get('login_count', 1)}")

    # 5. Dealers Breakdown
    if "dealers" in cols:
        print("\n" + "-" * 78)
        print("  5. VERIFIED SCRAP RECYCLERS & DEALERS")
        print("-" * 78)
        for d in db.dealers.find().limit(4):
            print(f"    * {d.get('name')} ({d.get('city')}, {d.get('state')}) | Tel: {d.get('phone')} | Rating: {d.get('rating')}/5.0 | Badge: {d.get('badge')}")

    # 6. Analytics Breakdown
    if "analytics" in cols:
        print("\n" + "-" * 78)
        print("  6. CIRCULAR ECONOMY & ANALYTICS")
        print("-" * 78)
        an = db.analytics.find_one() or {}
        print(f"    * Total Recycled Weight Managed : {an.get('total_scrap_inventory_weight_kg', 0):,.1f} kg")
        print(f"    * Total Disassembled Units     : {an.get('total_scrap_inventory_units', 0):,.0f} units")
        print(f"    * Estimated CO2 Offset Saved   : {an.get('estimated_co2_offset_tonnes', 0)} Tonnes")
        print(f"    * Precious Metal Recovery Rate : {an.get('precious_metals_recovery_rate', '99%')}")

    print("\n" + "=" * 78)
    print("  HOW TO DEMONSTRATE THIS DATABASE TO YOUR TEACHER:")
    print("=" * 78)
    print("  OPTION 1 (In Terminal / Command Prompt during viva):")
    print("    Command: python show_database.py")
    print("    This instantly displays live MongoDB status, collections, and records.\n")
    print("  OPTION 2 (In MongoDB Compass GUI - Visual Presentation):")
    print("    1. Open 'MongoDB Compass' application on this computer.")
    print("    2. In URI connection box, use: mongodb://127.0.0.1:27017")
    print("    3. Click 'Connect'.")
    print("    4. Click on database 'scrapsense'.")
    print("    5. Show the collections: categories (130), listings (30), orders (5), users, dealers, analytics.")
    print("=" * 78 + "\n")


if __name__ == "__main__":
    main()
