"""
ScrapSense AI - Comprehensive MongoDB Seeder
================================================
Populates all project data into MongoDB:
  1. categories: 130 authentic scrap materials with prices, tips, and eco metrics
  2. dealers: Verified Indian scrap dealer directory
  3. users: Administrator, verified scrap sellers, and enterprise buyers
  4. listings: 30 verified & pending scrap lots across all 6 categories
  5. orders: Transactions, admin-approved orders with payment receipts, and RFQs
  6. analytics: Circular economy impact and recycling summary metrics
"""

import os
import sys
import hashlib
import secrets
from pathlib import Path
from datetime import datetime, timezone
from pymongo import MongoClient

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from categories import WASTE_CATEGORIES, DEALER_DIRECTORY

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
DB_NAME = os.getenv("MONGODB_DATABASE", "scrapsense")


def hash_pw(password: str):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120000).hex()
    return salt, digest


def seed_database(seed_if_empty: bool = False, db=None):
    if db is None:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        print(f"[*] Connected to MongoDB: {MONGODB_URI} -> Database: '{DB_NAME}'")

    now = datetime.now(timezone.utc)

    # -------------------------------------------------------------
    # 1. CATEGORIES COLLECTION (130 items)
    # -------------------------------------------------------------
    print("\n[1/6] Checking 'categories' collection...")
    cat_count = db.categories.count_documents({})
    if cat_count == 0:
        cat_docs = []
        for label, info in WASTE_CATEGORIES.items():
            base_p = info.get("base_price", info.get("min_price", 0))
            unit = info.get("unit", "kg")
            doc = {
                "key": label,
                "display_name": info["display_name"],
                "category": info["category"],
                "type": info["type"],
                "unit": unit,
                "base_price": base_p,
                "min_price": info.get("min_price", 0),
                "max_price": info.get("max_price", 0),
                "spot_price": base_p,
                "price_range": f"₹{base_p} /{unit}",
                "sell_to": info.get("sell_to", "Authorized Recycler"),
                "reuse_tip": info.get("reuse_tip", ""),
                "eco_impact": info.get("eco_impact", {}),
                "icon": info.get("icon", "♻️"),
                "created_at": now,
                "updated_at": now
            }
            cat_docs.append(doc)
        
        if cat_docs:
            res = db.categories.insert_many(cat_docs)
            print(f"  --> Inserted {len(res.inserted_ids)} scrap items across all 6 categories into 'categories'.")
    else:
        print(f"  --> Preserving existing {cat_count} categories (no purge).")

    # -------------------------------------------------------------
    # 2. DEALERS COLLECTION
    # -------------------------------------------------------------
    print("\n[2/6] Checking 'dealers' collection...")
    dealer_count = db.dealers.count_documents({})
    if dealer_count == 0:
        dealers = [
        {
            "name": "EcoRecycle Tech Hub",
            "types": ["E-Waste", "Metal Scrap"],
            "city": "Pune",
            "state": "Maharashtra",
            "phone": "+91 98450 12345",
            "email": "contact@ecorecycle.in",
            "badge": "CPCB Certified E-Waste & Metal Recycler",
            "address": "Bhosari Industrial Area, Sector 7, MIDC, Pune 411026",
            "accepts": ["Old Computers", "Mobile Phones", "Motherboards", "CPUs", "Copper Wires", "Batteries"],
            "rating": 4.9,
            "verified": True
        },
        {
            "name": "Bharat Metal & Industrial Scrap Traders",
            "types": ["Metal Scrap", "Industrial Scrap"],
            "city": "Jaipur",
            "state": "Rajasthan",
            "phone": "+91 98200 67890",
            "email": "metals@bharatscrap.com",
            "badge": "Daily Mandi Spot Pricing · Weighbridge Certified",
            "address": "Loha Mandi, Heavy Metal Yard Sector 4, Jaipur 302013",
            "accepts": ["Scrap Iron", "Steel", "Copper Wire", "Brass", "Aluminium", "Automobile Parts", "Chemical Drums"],
            "rating": 4.8,
            "verified": True
        },
        {
            "name": "Swachh Polymer, Paper & Glass Aggregators",
            "types": ["Plastic Waste", "Paper & Cardboard", "Glass & Rubber"],
            "city": "Ahmedabad",
            "state": "Gujarat",
            "phone": "+91 93100 11223",
            "email": "info@swachhpolymer.org",
            "badge": "Bulk Doorstep Pickup & Digital Scale Certified",
            "address": "Eco Green Scrap Cluster #22, Naroda Industrial Estate, Ahmedabad 382330",
            "accepts": ["PET Bottles", "HDPE Buckets", "PVC Pipes", "Newspapers", "Cartons", "Glass Bottles", "Tyres"],
            "rating": 4.7,
            "verified": True
        },
        {
            "name": "Silicon City Electronic Refineries",
            "types": ["E-Waste"],
            "city": "Bengaluru",
            "state": "Karnataka",
            "phone": "+91 98860 44556",
            "email": "silicon@erefinery.in",
            "badge": "Hydrometallurgical Precious Metals Reclaim",
            "address": "Peenya 3rd Phase Industrial Area, Bengaluru 560058",
            "accepts": ["Server Boards", "Gold-Pin CPUs", "DDR RAM", "IC Chips", "Telecom Cards"],
            "rating": 4.9,
            "verified": True
        },
        {
            "name": "Capital Industrial Dismantlers & Salvage",
            "types": ["Industrial Scrap", "Metal Scrap"],
            "city": "Delhi",
            "state": "Delhi",
            "phone": "+91 98110 77889",
            "email": "capital.salvage@delhiscrap.org",
            "badge": "Demolition, Heavy Machinery & Plant Liquidation",
            "address": "Mayapuri Industrial Area Phase II, New Delhi 110064",
            "accepts": ["Motor Stators", "Engine Blocks", "HVAC Coils", "IBC Totes", "Factory Slag"],
            "rating": 4.8,
            "verified": True
        },
        {
            "name": "Deccan Rubber Crumb & Cullet Processors",
            "types": ["Glass & Rubber"],
            "city": "Chennai",
            "state": "Tamil Nadu",
            "phone": "+91 94440 33221",
            "email": "deccan.rubber@chennairubber.com",
            "badge": "Tire Pyrolysis & Glass Furnace Feedstock",
            "address": "Ambattur Industrial Estate, Chennai 600058",
            "accepts": ["Commercial TBR Tyres", "Flint Glass Cullet", "Crumb Granules", "Conveyor Belts"],
            "rating": 4.6,
            "verified": True
        }
    ]
    if dealer_count == 0:
        res = db.dealers.insert_many(dealers)
        print(f"  --> Inserted {len(res.inserted_ids)} scrap dealers into 'dealers'.")
    else:
        print(f"  --> Preserving existing {dealer_count} dealers (no purge).")

    # -------------------------------------------------------------
    # 3. USERS COLLECTION (Admin, Sellers, Buyers)
    # -------------------------------------------------------------
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
    """Resets users collection back to authentic default demonstration accounts."""
    if db is None:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
        db = client[DB_NAME]

    # Delete all users
    db.users.delete_many({})

    # Clear pending OTP requests and password resets
    try:
        db.otp_requests.delete_many({})
    except Exception:
        pass
    try:
        db.password_resets.delete_many({})
    except Exception:
        pass

    now = datetime.now(timezone.utc)
    for u in DEFAULT_USERS:
        salt, pw_hash = hash_pw(u["password"])
        db.users.update_one(
            {"email": u["email"].lower()},
            {"$set": {
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
            }},
            upsert=True
        )
    return len(DEFAULT_USERS)

    # -------------------------------------------------------------
    # 4. LISTINGS COLLECTION (30 lots: 24 verified + 6 pending)
    # -------------------------------------------------------------
    print("\n[4/6] Checking 'listings' collection...")
    listing_count = db.listings.count_documents({})
    all_lots = [
        # --- Metal Scrap (4 verified, 1 pending) ---
        {"seller": "Rajesh Sharma", "seller_email": "apex.metals@scrapsense.org", "item": "HMS 1&2 Heavy Melting Scrap", "category": "Metal Scrap", "unit": "kg", "quantity": 1500.0, "city": "Jaipur", "state": "Rajasthan", "note": "Clean 6mm+ industrial structural cuts, furnace-ready baled lots.", "min_price": 38.0, "max_price": 44.0, "verified": True},
        {"seller": "Rajesh Sharma", "seller_email": "apex.metals@scrapsense.org", "item": "Copper Millberry Bright Wire", "category": "Metal Scrap", "unit": "kg", "quantity": 240.0, "city": "Ahmedabad", "state": "Gujarat", "note": "99.9% pure stripped electrolytic copper wire scrap, unalloyed.", "min_price": 740.0, "max_price": 810.0, "verified": True},
        {"seller": "Western Alloys Yard", "seller_email": "western.alloys@scrapsense.org", "item": "Stainless Steel 304 Scrap", "category": "Metal Scrap", "unit": "kg", "quantity": 650.0, "city": "Pune", "state": "Maharashtra", "note": "Industrial kitchenware & dairy tank offcuts, clean non-magnetic SS 304.", "min_price": 130.0, "max_price": 155.0, "verified": True},
        {"seller": "Capital Extrusions", "seller_email": "capital.extrusions@scrapsense.org", "item": "Aluminium Extrusion 6063 Scrap", "category": "Metal Scrap", "unit": "kg", "quantity": 420.0, "city": "Delhi", "state": "Delhi", "note": "Clean architectural window sections, free of iron screws and gaskets.", "min_price": 185.0, "max_price": 215.0, "verified": True},
        {"seller": "Rajesh Sharma", "seller_email": "apex.metals@scrapsense.org", "item": "Brass Honey & Sanitary Scrap", "category": "Metal Scrap", "unit": "kg", "quantity": 180.0, "city": "Jaipur", "state": "Rajasthan", "note": "Plumbing and bathroom valve scrap, de-chromed.", "min_price": 340.0, "max_price": 380.0, "verified": False},

        # --- Plastic Waste (4 verified, 1 pending) ---
        {"seller": "Pooja Patel", "seller_email": "cleanpoly@scrapsense.org", "item": "Clean Clear PET Bottle Bales", "category": "Plastic Waste", "unit": "kg", "quantity": 800.0, "city": "Indore", "state": "Madhya Pradesh", "note": "Post-consumer clear PET bottles, caps removed, washed and hydraulic baled.", "min_price": 34.0, "max_price": 42.0, "verified": True},
        {"seller": "Pooja Patel", "seller_email": "cleanpoly@scrapsense.org", "item": "Rigid HDPE Drum & Crate Regrind", "category": "Plastic Waste", "unit": "kg", "quantity": 500.0, "city": "Jaipur", "state": "Rajasthan", "note": "Blue 200L drum regrind flakes, washed and dried, ready for extrusion.", "min_price": 52.0, "max_price": 64.0, "verified": True},
        {"seller": "UP Pipes & Conduits", "seller_email": "up.pipes@scrapsense.org", "item": "Rigid PVC Conduit Scrap", "category": "Plastic Waste", "unit": "kg", "quantity": 350.0, "city": "Kanpur", "state": "Uttar Pradesh", "note": "Factory electrical conduit pipe rejects, unplasticized PVC clean regrind.", "min_price": 32.0, "max_price": 40.0, "verified": True},
        {"seller": "Punjab Film Solutions", "seller_email": "pb.films@scrapsense.org", "item": "LDPE Packaging Film Rolls", "category": "Plastic Waste", "unit": "kg", "quantity": 600.0, "city": "Ludhiana", "state": "Punjab", "note": "Transparent pallet stretch wrap scrap, 100% natural clear grade.", "min_price": 48.0, "max_price": 58.0, "verified": True},
        {"seller": "Pooja Patel", "seller_email": "cleanpoly@scrapsense.org", "item": "PP Woven Jumbo Sacks (FIBC)", "category": "Plastic Waste", "unit": "kg", "quantity": 400.0, "city": "Indore", "state": "Madhya Pradesh", "note": "Clean 1-ton bulk bags, unprinted, baled.", "min_price": 28.0, "max_price": 35.0, "verified": False},

        # --- Paper & Cardboard (4 verified, 1 pending) ---
        {"seller": "Pink City Paper Pulp", "seller_email": "pinkcity.paper@scrapsense.org", "item": "Baled Corrugated Cartons (OCC 95/5)", "category": "Paper & Cardboard", "unit": "kg", "quantity": 2200.0, "city": "Jaipur", "state": "Rajasthan", "note": "High-burst corrugated cardboard boxes, mill baled, moisture under 10%.", "min_price": 14.0, "max_price": 18.0, "verified": True},
        {"seller": "Metro Paper Recyclers", "seller_email": "metro.paper@scrapsense.org", "item": "Sorted Office White Paper (SOW)", "category": "Paper & Cardboard", "unit": "kg", "quantity": 950.0, "city": "Delhi", "state": "Delhi", "note": "De-stapled office copier paper, records and invoices, woodfree white stock.", "min_price": 18.0, "max_price": 24.0, "verified": True},
        {"seller": "Deccan Newsprint Bales", "seller_email": "deccan.news@scrapsense.org", "item": "Old Newspapers (ONP Bales)", "category": "Paper & Cardboard", "unit": "kg", "quantity": 1200.0, "city": "Pune", "state": "Maharashtra", "note": "Sorted household and press return newspaper stacks, unsoiled.", "min_price": 14.0, "max_price": 17.0, "verified": True},
        {"seller": "Gujarat Board Yards", "seller_email": "gj.boards@scrapsense.org", "item": "Duplex Grey Board Offcuts", "category": "Paper & Cardboard", "unit": "kg", "quantity": 700.0, "city": "Ahmedabad", "state": "Gujarat", "note": "Clean box manufacturing trims, grey-back duplex board cuttings.", "min_price": 11.0, "max_price": 15.0, "verified": True},
        {"seller": "Pink City Paper Pulp", "seller_email": "pinkcity.paper@scrapsense.org", "item": "Printed Textbook & Notebook Trims", "category": "Paper & Cardboard", "unit": "kg", "quantity": 550.0, "city": "Jaipur", "state": "Rajasthan", "note": "Clean paper factory binding trimmings, woodfree white stock.", "min_price": 15.0, "max_price": 19.0, "verified": False},

        # --- E-Waste & Electronics (4 verified, 1 pending) ---
        {"seller": "Karthik Nair", "seller_email": "silicon.escrap@scrapsense.org", "item": "Dual-Socket Server Motherboards", "category": "E-Waste", "unit": "unit", "quantity": 180.0, "city": "Bengaluru", "state": "Karnataka", "note": "High-gold grade multi-socket enterprise server boards, BGA chips intact.", "min_price": 550.0, "max_price": 900.0, "verified": True},
        {"seller": "Karthik Nair", "seller_email": "silicon.escrap@scrapsense.org", "item": "DDR3/DDR4 Gold Finger RAM Modules", "category": "E-Waste", "unit": "unit", "quantity": 350.0, "city": "Pune", "state": "Maharashtra", "note": "Unsorted desktop and workstation memory DIMMs with clean gold pins.", "min_price": 85.0, "max_price": 145.0, "verified": True},
        {"seller": "Amit Verma", "seller_email": "greenpower@scrapsense.org", "item": "Defective Lithium-Ion 18650 Battery Cells", "category": "E-Waste", "unit": "kg", "quantity": 280.0, "city": "Delhi", "state": "Delhi", "note": "De-housed EV and power tool 18650 cells, sorted for black mass extraction.", "min_price": 140.0, "max_price": 195.0, "verified": True},
        {"seller": "CyberGold Refineries", "seller_email": "cybergold@scrapsense.org", "item": "Mixed Ceramic & Fiber CPUs", "category": "E-Waste", "unit": "unit", "quantity": 120.0, "city": "Hyderabad", "state": "Telangana", "note": "High-yield Intel/AMD 486, Pentium Pro and socket 775/1155 ceramic processor scrap.", "min_price": 220.0, "max_price": 480.0, "verified": True},
        {"seller": "Karthik Nair", "seller_email": "silicon.escrap@scrapsense.org", "item": "Telecom Base Station BTS Transceiver Cards", "category": "E-Waste", "unit": "unit", "quantity": 40.0, "city": "Bengaluru", "state": "Karnataka", "note": "Heavy gold-plated RF power amplifier boards.", "min_price": 400.0, "max_price": 750.0, "verified": False},

        # --- Glass & Rubber (4 verified, 1 pending) ---
        {"seller": "Tamil Nadu Crumb Industries", "seller_email": "tn.crumb@scrapsense.org", "item": "Crumb Rubber 30-Mesh Granules", "category": "Glass & Rubber", "unit": "kg", "quantity": 1400.0, "city": "Chennai", "state": "Tamil Nadu", "note": "Magnetic separated rubber granules, free of wire and fluff, ready for asphalt blending.", "min_price": 26.0, "max_price": 36.0, "verified": True},
        {"seller": "Suhaag Glass Works", "seller_email": "suhaag.glass@scrapsense.org", "item": "Clear Flint Glass Cullet (Sorted)", "category": "Glass & Rubber", "unit": "kg", "quantity": 3000.0, "city": "Firozabad", "state": "Uttar Pradesh", "note": "Color-sorted flint cullet from beverage bottling plants, washed and furnace ready.", "min_price": 3.5, "max_price": 5.5, "verified": True},
        {"seller": "Rajasthan Tyre Recyclers", "seller_email": "rj.tyres@scrapsense.org", "item": "Used Commercial TBR Truck Tyres", "category": "Glass & Rubber", "unit": "unit", "quantity": 80.0, "city": "Jaipur", "state": "Rajasthan", "note": "Heavy radial commercial vehicle casings suitable for pyrolysis distillation.", "min_price": 450.0, "max_price": 750.0, "verified": True},
        {"seller": "Mining Conveyor Salvage", "seller_email": "mining.conveyor@scrapsense.org", "item": "Industrial EPDM Rubber Conveyor Belt Scrap", "category": "Glass & Rubber", "unit": "kg", "quantity": 900.0, "city": "Ranchi", "state": "Jharkhand", "note": "Heavy-duty 4-ply rubber conveyor belt strips salvaged from iron ore washeries.", "min_price": 16.0, "max_price": 24.0, "verified": True},
        {"seller": "Suhaag Glass Works", "seller_email": "suhaag.glass@scrapsense.org", "item": "Amber Beer Bottles Sorted Lots", "category": "Glass & Rubber", "unit": "kg", "quantity": 1200.0, "city": "Firozabad", "state": "Uttar Pradesh", "note": "Intact 650ml amber beer bottles, washed and crate-packed.", "min_price": 3.8, "max_price": 5.0, "verified": False},

        # --- Industrial Scrap (4 verified, 1 pending) ---
        {"seller": "Coimbatore Electro-Motors", "seller_email": "cbe.motors@scrapsense.org", "item": "Burned Cast Iron Motor Stators", "category": "Industrial Scrap", "unit": "kg", "quantity": 450.0, "city": "Coimbatore", "state": "Tamil Nadu", "note": "Heavy 3-phase industrial motor housings with complete copper stator windings.", "min_price": 85.0, "max_price": 115.0, "verified": True},
        {"seller": "Baroda Chemical Packaging", "seller_email": "baroda.drums@scrapsense.org", "item": "Industrial 200-Litre HDPE Drums", "category": "Industrial Scrap", "unit": "unit", "quantity": 160.0, "city": "Vadodara", "state": "Gujarat", "note": "Triple-rinsed neutral chemical storage barrels, unpunctured with bungs intact.", "min_price": 320.0, "max_price": 460.0, "verified": True},
        {"seller": "Saurashtra Foundry Scrap", "seller_email": "saurashtra.foundry@scrapsense.org", "item": "Rotary Machine Tool Bed Castings", "category": "Industrial Scrap", "unit": "kg", "quantity": 1800.0, "city": "Rajkot", "state": "Gujarat", "note": "Heavy grade 25 grey cast iron machine bed cuts, zero slag or porosity.", "min_price": 36.0, "max_price": 42.0, "verified": True},
        {"seller": "Capital HVAC Dismantlers", "seller_email": "capital.hvac@scrapsense.org", "item": "Copper Tube & Aluminium Fin HVAC Coils", "category": "Industrial Scrap", "unit": "kg", "quantity": 320.0, "city": "Delhi", "state": "Delhi", "note": "Chiller and VRF indoor unit heat exchanger coils, dry clean metal.", "min_price": 310.0, "max_price": 370.0, "verified": True},
        {"seller": "Baroda Chemical Packaging", "seller_email": "baroda.drums@scrapsense.org", "item": "1000-Litre Composite IBC Totes", "category": "Industrial Scrap", "unit": "unit", "quantity": 25.0, "city": "Vadodara", "state": "Gujarat", "note": "Galvanized steel tubular grid frame with blow-moulded HDPE bottle.", "min_price": 1800.0, "max_price": 2600.0, "verified": False}
    ]

    if listing_count == 0:
        for lot in all_lots:
            lot["created_at"] = now
            lot["verified_at"] = now if lot["verified"] else None
            lot["photo"] = ""
            lot["ownerEmail"] = lot["seller_email"]

        res = db.listings.insert_many(all_lots)
        print(f"  --> Inserted {len(res.inserted_ids)} scrap lots into 'listings' (24 verified + 6 pending admin approval).")
    else:
        print(f"  --> Preserving existing {listing_count} marketplace listings (no purge).")

    # -------------------------------------------------------------
    # 5. ORDERS COLLECTION (Transactions, Approvals & RFQs)
    # -------------------------------------------------------------
    print("\n[5/6] Checking 'orders' collection...")
    order_count = db.orders.count_documents({})
    orders = [
        # Completed / Admin-Approved Order 1
        {
            "lot": "Dual-Socket Server Motherboards",
            "item": "Dual-Socket Server Motherboards",
            "category": "E-Waste",
            "buyer": "Dr. Ananya Roy - EcoRecycle Smelters",
            "buyer_name": "Dr. Ananya Roy",
            "buyer_email": "purchase@ecorecycle.in",
            "seller": "Karthik Nair",
            "seller_email": "silicon.escrap@scrapsense.org",
            "quantity": 50.0,
            "unit": "unit",
            "offered_price": 720.0,
            "min_price": 550.0,
            "max_price": 900.0,
            "payment": "Bank RTGS / NEFT",
            "payment_method": "Bank RTGS / NEFT",
            "address": "EcoRecycle Smelters Hydrometallurgy Unit, Bhosari MIDC, Pune, Maharashtra",
            "status": "Admin approved - seller notified",
            "buyer_decision": "accepted",
            "created_at": now,
            "decided_at": now
        },
        # Completed / Admin-Approved Order 2
        {
            "lot": "HMS 1&2 Heavy Melting Scrap",
            "item": "HMS 1&2 Heavy Melting Scrap",
            "category": "Metal Scrap",
            "buyer": "Sunil Mehta - Tata Steel Circularity",
            "buyer_name": "Sunil Mehta",
            "buyer_email": "procurement@tatasteel.com",
            "seller": "Rajesh Sharma",
            "seller_email": "apex.metals@scrapsense.org",
            "quantity": 1000.0,
            "unit": "kg",
            "offered_price": 42.0,
            "min_price": 38.0,
            "max_price": 44.0,
            "payment": "Pay on Weighbridge Delivery",
            "payment_method": "Pay on Weighbridge Delivery",
            "address": "Tata Steel Plant Inward Weighbridge, Jamshedpur / Navi Mumbai",
            "status": "Admin approved - seller notified",
            "buyer_decision": "accepted",
            "created_at": now,
            "decided_at": now
        },
        # Pending Approval Order 1 (demonstrable in Admin dashboard)
        {
            "lot": "Clean Clear PET Bottle Bales",
            "item": "Clean Clear PET Bottle Bales",
            "category": "Plastic Waste",
            "buyer": "Vikram Singhania - Reliance Polymer Reclaim",
            "buyer_name": "Vikram Singhania",
            "buyer_email": "buyer.polymers@ril.com",
            "seller": "Pooja Patel",
            "seller_email": "cleanpoly@scrapsense.org",
            "quantity": 500.0,
            "unit": "kg",
            "offered_price": 38.0,
            "min_price": 34.0,
            "max_price": 42.0,
            "payment": "UPI",
            "payment_method": "UPI",
            "address": "Reliance Recycled Polyester Fiber Plant, Dahej, Gujarat",
            "status": "Buyer accepted - Admin approval pending",
            "buyer_decision": "accepted",
            "created_at": now
        },
        # Pending Approval Order 2
        {
            "lot": "Copper Millberry Bright Wire",
            "item": "Copper Millberry Bright Wire",
            "category": "Metal Scrap",
            "buyer": "Sunil Mehta - Tata Steel Circularity",
            "buyer_name": "Sunil Mehta",
            "buyer_email": "procurement@tatasteel.com",
            "seller": "Rajesh Sharma",
            "seller_email": "apex.metals@scrapsense.org",
            "quantity": 120.0,
            "unit": "kg",
            "offered_price": 780.0,
            "min_price": 740.0,
            "max_price": 810.0,
            "payment": "Bank RTGS / NEFT",
            "payment_method": "Bank RTGS / NEFT",
            "address": "Tata Steel Inward Material Gate, Tarapur Industrial Area",
            "status": "Buyer accepted - Admin approval pending",
            "buyer_decision": "accepted",
            "created_at": now
        },
        # Buyer B2B Procurement RFQ
        {
            "lot": "Rigid PVC Conduit Scrap - White Regrind",
            "item": "Rigid PVC Conduit Scrap - White Regrind",
            "category": "Plastic Waste",
            "buyer": "Vikram Singhania - Reliance Polymer Reclaim",
            "buyer_name": "Vikram Singhania",
            "buyer_email": "buyer.polymers@ril.com",
            "seller": "Admin Matched Network",
            "seller_email": "",
            "quantity": 2500.0,
            "unit": "kg",
            "offered_price": 36.0,
            "payment": "Letter of Credit (LC)",
            "payment_method": "Letter of Credit (LC)",
            "address": "Plot 42, GIDC Industrial Estate, Naroda, Ahmedabad, Gujarat",
            "status": "Buyer RFQ Submitted - Admin Matching",
            "note": "Urgent requirement for pipe extrusion. Unplasticized white regrind only.",
            "created_at": now
        },
        # B2B Seller Sell Request - Pending Buyer Approval
        {
            "type": "sell_request",
            "item": "Copper Wire Millberry Scrap",
            "category": "Metal Scrap",
            "seller": "Rajesh Sharma",
            "seller_name": "Rajesh Sharma",
            "seller_email": "apex.metals@scrapsense.org",
            "seller_phone": "+91 98290 11223",
            "quantity": 250.0,
            "unit": "kg",
            "expected_price": 760.0,
            "total_expected_value": 190000.0,
            "city": "Jaipur",
            "state": "Rajasthan",
            "address": "Godown 14, Vishwakarma Industrial Area (VKIA), Road No. 9, Jaipur",
            "note": "99.9% bare clean bright copper wire scrap, unburnt, zero grease.",
            "status": "Pending Buyer Approval",
            "created_at": now
        },
        # B2B Deal - Buyer Approved, Awaiting Admin Clearance
        {
            "type": "sell_request",
            "item": "Dual-Socket Server Motherboards & High-Gold E-Scrap",
            "category": "E-Waste",
            "seller": "Karthik Nair",
            "seller_name": "Karthik Nair",
            "seller_email": "silicon.escrap@scrapsense.org",
            "seller_phone": "+91 98450 33445",
            "quantity": 300.0,
            "unit": "unit",
            "expected_price": 850.0,
            "total_expected_value": 255000.0,
            "city": "Bengaluru",
            "state": "Karnataka",
            "address": "Electronics City Phase 1, Near Toll Gate, Bengaluru",
            "note": "De-racked enterprise server boards, high yield gold pins and BGA chips intact.",
            "status": "Buyer Approved · Awaiting Admin Clearance",
            "buyer_name": "Dr. Ananya Roy",
            "buyer_email": "purchase@ecorecycle.in",
            "agreed_price": 880.0,
            "deal_amount": 264000.0,
            "delivery_type": "Seller Delivery to Warehouse",
            "delivery_schedule": "Within 3 Days",
            "delivery_address": "EcoRecycle Smelters Hydrometallurgy Unit, Bhosari MIDC, Pune, Maharashtra",
            "payment_terms": "Instant RTGS / Bank Transfer on Weighment",
            "deal_notes": "MoEFCC manifest required upon delivery. Gold yield sampling to be executed at lab.",
            "buyer_approved_at": now,
            "created_at": now
        },
        # B2B Deal - Admin Cleared & Active with Official Contract
        {
            "type": "sell_request",
            "item": "HMS 1&2 Heavy Melting Steel Scrap",
            "category": "Metal Scrap",
            "seller": "Rajesh Sharma",
            "seller_name": "Rajesh Sharma",
            "seller_email": "apex.metals@scrapsense.org",
            "seller_phone": "+91 98290 11223",
            "quantity": 25000.0,
            "unit": "kg",
            "expected_price": 42.0,
            "total_expected_value": 1050000.0,
            "city": "Jaipur",
            "state": "Rajasthan",
            "address": "VKIA Road 14 Inward Yard, Jaipur",
            "status": "Admin Cleared & Verified · Deal Active",
            "buyer_name": "Sunil Mehta",
            "buyer_email": "procurement@tatasteel.com",
            "agreed_price": 44.0,
            "deal_amount": 1100000.0,
            "delivery_type": "Platform Certified Transporter",
            "delivery_schedule": "Immediate (Within 24 Hours)",
            "delivery_address": "Tata Steel Plant Inward Weighbridge Gate 2, Tarapur / Navi Mumbai",
            "payment_terms": "50% Advance + 50% on Weighbridge Gate Pass",
            "deal_notes": "Verified 6mm+ heavy cuts. Clean melting grade.",
            "admin_cleared": True,
            "admin_cleared_by": "admin@scrapsense.org",
            "admin_cleared_at": now,
            "contract_id": "CTR-202609-77821",
            "buyer_approved_at": now,
            "created_at": now
        }
    ]
    if order_count == 0:
        res = db.orders.insert_many(orders)
        print(f"  --> Inserted {len(res.inserted_ids)} transactions into 'orders'.")
    else:
        print(f"  --> Preserving existing {order_count} user orders (no purge).")

    # -------------------------------------------------------------
    # 6. ANALYTICS & RECYCLING METRICS
    # -------------------------------------------------------------
    print("\n[6/6] Checking 'analytics' collection...")
    analytics_count = db.analytics.count_documents({})
    if seed_if_empty and analytics_count > 0:
        print(f"  --> Preserving existing analytics (seed-if-empty mode).")
    else:
        analytics_doc = {
            "platform_name": "ScrapSense AI",
            "version": "2.0.0",
            "total_categories_tracked": len(cat_docs) if 'cat_docs' in locals() else 130,
            "total_active_dealers": len(dealers) if 'dealers' in locals() else dealer_count,
            "total_registered_users": len(users),
            "total_scrap_inventory_weight_kg": sum(l["quantity"] for l in all_lots if l.get("unit") == "kg"),
            "total_scrap_inventory_units": sum(l["quantity"] for l in all_lots if l.get("unit") == "unit"),
            "estimated_co2_offset_tonnes": 48.6,
            "precious_metals_recovery_rate": "99.2%",
            "active_mandi_cities": ["Pune", "Mumbai", "Delhi", "Jaipur", "Ahmedabad", "Bengaluru", "Chennai", "Hyderabad", "Kanpur", "Kolkata"],
            "ai_model": "OpenAI CLIP ViT-B/32 Zero-Shot + Heuristic Pricing Engine",
            "updated_at": now
        }
        db.analytics.update_one({"platform_name": "ScrapSense AI"}, {"$set": analytics_doc}, upsert=True)
        print("  --> Platform analytics & circular metrics synchronized.")

    print("\n" + "=" * 65)
    print("  DATABASE SEEDING COMPLETED SUCCESSFULLY!")
    print(f"  Database '{DB_NAME}' is completely populated with all data.")
    print("=" * 65)

    # Print summary table
    if hasattr(db, "list_collection_names"):
        try:
            print("\nSummary of Collections in MongoDB:")
            for col in sorted(db.list_collection_names()):
                count = db[col].count_documents({})
                print(f"  • {col:18} : {count:4} documents")
        except Exception:
            pass


if __name__ == "__main__":
    seed_database()
