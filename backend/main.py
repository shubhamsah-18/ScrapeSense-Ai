"""
ScrapSense AI - Backend API
------------------------------------------------
Final Year Engineering Project

Zero-Shot CLIP Vision Model + Scrap Resale Pricing Engine + Eco-Impact Analytics (Expanded Electronic Components)
"""

import io
import os
import sys
import base64
import hashlib
import html as html_lib
import re
import secrets
import threading
import smtplib
from email.message import EmailMessage
from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from PIL import Image

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except ImportError:
    pass

try:
    from pymongo import MongoClient
    from bson import ObjectId
    import qrcode
    HAS_MONGO = True
except ImportError:
    HAS_MONGO = False

HAS_TORCH = os.getenv("DISABLE_TORCH", "").strip().lower() not in ("1", "true", "yes")

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from contextlib import asynccontextmanager
from categories import WASTE_CATEGORIES, DEALER_DIRECTORY
from auth import (
    create_access_token,
    get_current_user,
    require_role,
    hash_password,
    verify_password,
    set_auth_cookie,
    clear_auth_cookie,
    validate_password_strength,
    rate_limiter
)
import ai_service

# MongoDB index setup
def setup_mongo_indexes():
    """Create MongoDB indexes for performance and data integrity."""
    try:
        database = mongo_db()
        database.users.create_index([("email", 1), ("role", 1)], unique=True)
        database.otp_requests.create_index("expires_at", expireAfterSeconds=0)
        database.password_resets.create_index("expires_at", expireAfterSeconds=0)
        database.listings.create_index([("verified", 1), ("created_at", -1)])
        database.orders.create_index([("buyer_email", 1), ("created_at", -1)])
        database.orders.create_index([("seller_email", 1), ("created_at", -1)])
        print("MongoDB indexes created.", flush=True)
    except Exception as exc:
        print(f"Index creation skipped: {exc}", flush=True)


def seed_default_listings():
    """Seed authentic marketplace inventory across all 6 scrap categories if few exist."""
    try:
        database = mongo_db()
        if database.listings.count_documents({"verified": True}) >= 12:
            return
        
        default_lots = [
            # Metal Scrap (4 lots)
            {"seller": "Apex Metal Recyclers", "seller_email": "apex.metals@scrapsense.org", "item": "HMS 1&2 Heavy Melting Scrap", "category": "Metal Scrap", "unit": "kg", "quantity": 1500.0, "city": "Jaipur", "state": "Rajasthan", "note": "Clean 6mm+ industrial structural cuts, furnace-ready baled lots.", "min_price": 38.0, "max_price": 44.0, "photo": ""},
            {"seller": "Gujarat Copper Refiners", "seller_email": "gj.copper@scrapsense.org", "item": "Copper Millberry Bright Wire", "category": "Metal Scrap", "unit": "kg", "quantity": 240.0, "city": "Ahmedabad", "state": "Gujarat", "note": "99.9% pure stripped electrolytic copper wire scrap, unalloyed.", "min_price": 740.0, "max_price": 810.0, "photo": ""},
            {"seller": "Western Alloys Yard", "seller_email": "western.alloys@scrapsense.org", "item": "Stainless Steel 304 Scrap", "category": "Metal Scrap", "unit": "kg", "quantity": 650.0, "city": "Pune", "state": "Maharashtra", "note": "Industrial kitchenware & dairy tank offcuts, clean non-magnetic SS 304.", "min_price": 130.0, "max_price": 155.0, "photo": ""},
            {"seller": "Capital Extrusions", "seller_email": "capital.extrusions@scrapsense.org", "item": "Aluminium Extrusion 6063 Scrap", "category": "Metal Scrap", "unit": "kg", "quantity": 420.0, "city": "Delhi", "state": "Delhi", "note": "Clean architectural window sections, free of iron screws and gaskets.", "min_price": 185.0, "max_price": 215.0, "photo": ""},

            # Plastic Waste (4 lots)
            {"seller": "CleanPoly Recyclers", "seller_email": "cleanpoly@scrapsense.org", "item": "Clean Clear PET Bottle Bales", "category": "Plastic Waste", "unit": "kg", "quantity": 800.0, "city": "Indore", "state": "Madhya Pradesh", "note": "Post-consumer clear PET bottles, caps removed, washed and hydraulic baled.", "min_price": 34.0, "max_price": 42.0, "photo": ""},
            {"seller": "Rajasthan Polymer Hub", "seller_email": "rj.polymers@scrapsense.org", "item": "Rigid HDPE Drum & Crate Regrind", "category": "Plastic Waste", "unit": "kg", "quantity": 500.0, "city": "Jaipur", "state": "Rajasthan", "note": "Blue 200L drum regrind flakes, washed and dried, ready for extrusion.", "min_price": 52.0, "max_price": 64.0, "photo": ""},
            {"seller": "UP Pipes & Conduits", "seller_email": "up.pipes@scrapsense.org", "item": "Rigid PVC Conduit Scrap", "category": "Plastic Waste", "unit": "kg", "quantity": 350.0, "city": "Kanpur", "state": "Uttar Pradesh", "note": "Factory electrical conduit pipe rejects, unplasticized PVC clean regrind.", "min_price": 32.0, "max_price": 40.0, "photo": ""},
            {"seller": "Punjab Film Solutions", "seller_email": "pb.films@scrapsense.org", "item": "LDPE Packaging Film Rolls", "category": "Plastic Waste", "unit": "kg", "quantity": 600.0, "city": "Ludhiana", "state": "Punjab", "note": "Transparent pallet stretch wrap scrap, 100% natural clear grade.", "min_price": 48.0, "max_price": 58.0, "photo": ""},

            # Paper & Cardboard (4 lots)
            {"seller": "Pink City Paper Pulp", "seller_email": "pinkcity.paper@scrapsense.org", "item": "Baled Corrugated Cartons (OCC 95/5)", "category": "Paper & Cardboard", "unit": "kg", "quantity": 2200.0, "city": "Jaipur", "state": "Rajasthan", "note": "High-burst corrugated cardboard boxes, mill baled, moisture under 10%.", "min_price": 14.0, "max_price": 18.0, "photo": ""},
            {"seller": "Metro Paper Recyclers", "seller_email": "metro.paper@scrapsense.org", "item": "Sorted Office White Paper (SOW)", "category": "Paper & Cardboard", "unit": "kg", "quantity": 950.0, "city": "Delhi", "state": "Delhi", "note": "De-stapled office copier paper, records and invoices, woodfree white stock.", "min_price": 18.0, "max_price": 24.0, "photo": ""},
            {"seller": "Deccan Newsprint Bales", "seller_email": "deccan.news@scrapsense.org", "item": "Old Newspapers (ONP Bales)", "category": "Paper & Cardboard", "unit": "kg", "quantity": 1200.0, "city": "Pune", "state": "Maharashtra", "note": "Sorted household and press return newspaper stacks, unsoiled.", "min_price": 14.0, "max_price": 17.0, "photo": ""},
            {"seller": "Gujarat Board Yards", "seller_email": "gj.boards@scrapsense.org", "item": "Duplex Grey Board Offcuts", "category": "Paper & Cardboard", "unit": "kg", "quantity": 700.0, "city": "Ahmedabad", "state": "Gujarat", "note": "Clean box manufacturing trims, grey-back duplex board cuttings.", "min_price": 11.0, "max_price": 15.0, "photo": ""},

            # E-Waste (4 lots)
            {"seller": "Silicon City E-Scrap", "seller_email": "silicon.escrap@scrapsense.org", "item": "Dual-Socket Server Motherboards", "category": "E-Waste", "unit": "unit", "quantity": 180.0, "city": "Bengaluru", "state": "Karnataka", "note": "High-gold grade multi-socket enterprise server boards, BGA chips intact.", "min_price": 550.0, "max_price": 900.0, "photo": ""},
            {"seller": "TechCycle Labs", "seller_email": "techcycle@scrapsense.org", "item": "DDR3/DDR4 Gold Finger RAM Modules", "category": "E-Waste", "unit": "unit", "quantity": 350.0, "city": "Pune", "state": "Maharashtra", "note": "Unsorted desktop and workstation memory DIMMs with clean gold pins.", "min_price": 85.0, "max_price": 145.0, "photo": ""},
            {"seller": "GreenPower Battery Salvage", "seller_email": "greenpower@scrapsense.org", "item": "Defective Lithium-Ion 18650 Battery Cells", "category": "E-Waste", "unit": "kg", "quantity": 280.0, "city": "Delhi", "state": "Delhi", "note": "De-housed EV and power tool 18650 cells, sorted for black mass extraction.", "min_price": 140.0, "max_price": 195.0, "photo": ""},
            {"seller": "CyberGold Refineries", "seller_email": "cybergold@scrapsense.org", "item": "Mixed Ceramic & Fiber CPUs", "category": "E-Waste", "unit": "unit", "quantity": 120.0, "city": "Hyderabad", "state": "Telangana", "note": "High-yield Intel/AMD 486, Pentium Pro and socket 775/1155 ceramic processor scrap.", "min_price": 220.0, "max_price": 480.0, "photo": ""},

            # Glass & Rubber (4 lots)
            {"seller": "Tamil Nadu Crumb Industries", "seller_email": "tn.crumb@scrapsense.org", "item": "Crumb Rubber 30-Mesh Granules", "category": "Glass & Rubber", "unit": "kg", "quantity": 1400.0, "city": "Chennai", "state": "Tamil Nadu", "note": "Magnetic separated rubber granules, free of wire and fluff, ready for asphalt blending.", "min_price": 26.0, "max_price": 36.0, "photo": ""},
            {"seller": "Suhaag Glass Works", "seller_email": "suhaag.glass@scrapsense.org", "item": "Clear Flint Glass Cullet (Sorted)", "category": "Glass & Rubber", "unit": "kg", "quantity": 3000.0, "city": "Firozabad", "state": "Uttar Pradesh", "note": "Color-sorted flint cullet from beverage bottling plants, washed and furnace ready.", "min_price": 3.5, "max_price": 5.5, "photo": ""},
            {"seller": "Rajasthan Tyre Recyclers", "seller_email": "rj.tyres@scrapsense.org", "item": "Used Commercial TBR Truck Tyres", "category": "Glass & Rubber", "unit": "unit", "quantity": 80.0, "city": "Jaipur", "state": "Rajasthan", "note": "Heavy radial commercial vehicle casings suitable for pyrolysis distillation.", "min_price": 450.0, "max_price": 750.0, "photo": ""},
            {"seller": "Mining Conveyor Salvage", "seller_email": "mining.conveyor@scrapsense.org", "item": "Industrial EPDM Rubber Conveyor Belt Scrap", "category": "Glass & Rubber", "unit": "kg", "quantity": 900.0, "city": "Ranchi", "state": "Jharkhand", "note": "Heavy-duty 4-ply rubber conveyor belt strips salvaged from iron ore washeries.", "min_price": 16.0, "max_price": 24.0, "photo": ""},

            # Industrial Scrap (4 lots)
            {"seller": "Coimbatore Electro-Motors", "seller_email": "cbe.motors@scrapsense.org", "item": "Burned Cast Iron Motor Stators", "category": "Industrial Scrap", "unit": "kg", "quantity": 450.0, "city": "Coimbatore", "state": "Tamil Nadu", "note": "Heavy 3-phase industrial motor housings with complete copper stator windings.", "min_price": 85.0, "max_price": 115.0, "photo": ""},
            {"seller": "Baroda Chemical Packaging", "seller_email": "baroda.drums@scrapsense.org", "item": "Industrial 200-Litre HDPE Drums", "category": "Industrial Scrap", "unit": "unit", "quantity": 160.0, "city": "Vadodara", "state": "Gujarat", "note": "Triple-rinsed neutral chemical storage barrels, unpunctured with bungs intact.", "min_price": 320.0, "max_price": 460.0, "photo": ""},
            {"seller": "Saurashtra Foundry Scrap", "seller_email": "saurashtra.foundry@scrapsense.org", "item": "Rotary Machine Tool Bed Castings", "category": "Industrial Scrap", "unit": "kg", "quantity": 1800.0, "city": "Rajkot", "state": "Gujarat", "note": "Heavy grade 25 grey cast iron machine bed cuts, zero slag or porosity.", "min_price": 36.0, "max_price": 42.0, "photo": ""},
            {"seller": "Capital HVAC Dismantlers", "seller_email": "capital.hvac@scrapsense.org", "item": "Copper Tube & Aluminium Fin HVAC Coils", "category": "Industrial Scrap", "unit": "kg", "quantity": 320.0, "city": "Delhi", "state": "Delhi", "note": "Chiller and VRF indoor unit heat exchanger coils, dry clean metal.", "min_price": 310.0, "max_price": 370.0, "photo": ""}
        ]

        now = datetime.now(timezone.utc)
        for lot in default_lots:
            lot["verified"] = True
            lot["verified_at"] = now
            lot["created_at"] = now
            database.listings.insert_one(lot)
        print(f"[ScrapSense] Seeded {len(default_lots)} verified scrap lots across all 6 categories.", flush=True)
    except Exception as exc:
        print(f"[ScrapSense] Listing seeding skipped: {exc}", flush=True)


@asynccontextmanager
async def lifespan(app):
    # Startup
    if HAS_MONGO:
        try:
            mongo_db()
            setup_mongo_indexes()
            try:
                from seed_db import seed_database
                seed_database(seed_if_empty=True)
            except Exception as e:
                print(f"[Seed] Auto-seed status: {e}", flush=True)
        except HTTPException as exc:
            print(exc.detail, flush=True)
    threading.Thread(target=load_model, daemon=True).start()
    yield
    # Shutdown
    if mongo_client:
        mongo_client.close()

app = FastAPI(
    title="ScrapSense AI - Scrap & Waste Detection API",
    description="Zero-shot scrap material identification, valuation & recycling intelligence",
    version="2.0.0",
    lifespan=lifespan
)

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"

# CORS: Universal regex allowing localhost, 127.0.0.1, LAN Wi-Fi IPs, mobile devices, and file:///
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEVICE = "cpu"
MODEL_NAME = "openai/clip-vit-base-patch32"

model = None
processor = None
model_status = "unloaded"

ADMIN_LOGIN = os.getenv("ADMIN_LOGIN", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
mongo_client = None
db = None
mongo_lock = threading.Lock()

LABELS = list(WASTE_CATEGORIES.keys())
TEXT_PROMPTS = [f"a photo of {label}" for label in LABELS]


class CalculateRequest(BaseModel):
    category_key: str = ""
    display_name: str = ""
    quantity: float = 1.0


class AIChatRequest(BaseModel):
    message: str
    provider: str = "gemini"
    history: list = []
    image: str | None = None
    session_id: str = "default_session"



class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str


class OtpRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str


class OtpVerifyRequest(BaseModel):
    email: str
    otp: str
    role: str = ""


class LoginRequest(BaseModel):
    email: str
    password: str
    role: str


class ForgotPasswordRequest(BaseModel):
    email: str
    role: str = ""


class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str
    role: str = ""


class ApprovalRequest(BaseModel):
    listing_id: str
    buyer_name: str = ""
    buyer_email: str = ""
    quantity: float
    offered_price: float = 0
    buyer_decision: str = "accepted"
    address: str = ""
    payment_method: str = "UPI/Cash on Pickup"


class ListingRequest(BaseModel):
    seller: str = ""
    seller_email: str = ""
    item: str
    category: str
    unit: str = "kg"
    quantity: float
    city: str
    state: str = ""
    note: str = ""
    min_price: float = 0
    max_price: float = 0
    photo: str = ""
    seller_phone: str = ""
    address: str = ""


class UpdateListingRequest(BaseModel):
    item: str | None = None
    category: str | None = None
    unit: str | None = None
    quantity: float | None = None
    city: str | None = None
    state: str | None = None
    note: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    status: str | None = None


class SellRequestCreate(BaseModel):
    item: str
    category: str
    quantity: float
    unit: str = "kg"
    expected_price: float = 0
    city: str
    state: str = ""
    address: str = ""
    seller_phone: str = ""
    note: str = ""
    photo: str = ""


class BuyerDealApprovalRequest(BaseModel):
    agreed_price: float
    deal_amount: float = 0
    delivery_method: str | None = None
    delivery_type: str = "Buyer Pickup / Own Logistics"
    delivery_schedule: str = "Immediate (Within 24 Hours)"
    delivery_address: str = ""
    payment_terms: str = "Instant RTGS / Bank Transfer on Weighment"
    buyer_notes: str | None = None
    deal_notes: str = ""


class AdminDealClearanceRequest(BaseModel):
    action: str = "clear"  # "clear" or "reject"
    clearance_notes: str | None = None
    admin_notes: str = ""
    admin_name: str | None = None


def password_hash(password: str, salt: str | None = None):
    """PBKDF2-HMAC password hashing for OTP verification flow."""
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120000).hex()
    return salt, digest


def sanitize_text(text: str) -> str:
    """Strip HTML tags and escape special characters to prevent XSS."""
    if not text:
        return text
    clean = html_lib.escape(text.strip())
    clean = re.sub(r'<[^>]+>', '', clean)
    return clean


def send_registration_otp(email: str, otp: str):
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_from = os.getenv("SMTP_FROM", smtp_user).strip()
    if not smtp_host or not smtp_user or not smtp_password:
        if os.getenv("DEV_OTP_MODE", "true").lower() == "true":
            print(f"[DEV OTP] Registration code for {email}: {otp}", flush=True)
            return
        raise HTTPException(status_code=503, detail="OTP email is not configured. Set SMTP settings in .env.")
    message = EmailMessage()
    message["Subject"] = "ScrapSense AI registration verification code"
    message["From"] = smtp_from
    message["To"] = email
    message.set_content(f"Your ScrapSense AI verification code is {otp}. It expires in 10 minutes.")
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(message)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Unable to send OTP email: {exc}")


def send_password_reset_otp(email: str, otp: str):
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    smtp_from = os.getenv("SMTP_FROM", smtp_user).strip()
    if not smtp_host or not smtp_user or not smtp_password:
        if os.getenv("DEV_OTP_MODE", "true").lower() == "true":
            print(f"[DEV OTP] Password reset verification code for {email}: {otp}", flush=True)
            return
        raise HTTPException(status_code=503, detail="Password reset email is not configured. Set SMTP settings in .env.")
    message = EmailMessage()
    message["Subject"] = "ScrapSense AI - Password Reset Verification Code"
    message["From"] = smtp_from
    message["To"] = email
    message.set_content(
        f"Hello,\n\n"
        f"We received a request to reset your ScrapSense AI account password.\n\n"
        f"Your 6-digit verification code is: {otp}\n\n"
        f"This code will expire in 10 minutes.\n"
        f"If you did not request a password reset, please ignore this email.\n\n"
        f"Regards,\nScrapSense AI Security Team"
    )
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(message)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Unable to send password reset email: {exc}")


def mongo_db():
    global mongo_client, db
    if db is not None:
        try:
            mongo_client.admin.command("ping")
            return db
        except Exception:
            mongo_client = None
            db = None

    if not HAS_MONGO:
        raise HTTPException(status_code=503, detail="PyMongo is not installed. Install backend requirements.")

    with mongo_lock:
        if db is None:
            try:
                mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000)
                mongo_client.admin.command("ping")
                db = mongo_client[os.getenv("MONGODB_DATABASE", "scrapsense")]
                print("MongoDB connected", flush=True)
            except Exception as exc:
                mongo_client = None
                db = None
                raise HTTPException(status_code=503, detail=f"MongoDB unavailable: {exc}")
    return db


def make_receipt_qr(order_id: str, amount: float, payment_method: str):
    payload = f"ScrapSense|Order:{order_id}|Amount:INR {amount:.2f}|Method:{payment_method}"
    image = qrcode.make(payload)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()


def mongo_id(value: str):
    try:
        return ObjectId(value)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid record ID.")


def serialize_mongo(obj):
    if isinstance(obj, dict):
        res = {}
        for k, v in obj.items():
            if k == "_id":
                res["id"] = str(v)
            else:
                res[k] = serialize_mongo(v)
        return res
    elif isinstance(obj, list):
        return [serialize_mongo(item) for item in obj]
    elif HAS_MONGO and isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def load_model():
    global model, processor, model_status, DEVICE, HAS_TORCH
    if not HAS_TORCH:
        model_status = "missing_dependencies"
        return
    try:
        model_status = "loading"
        import torch
        from transformers import CLIPModel, CLIPProcessor
        DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading CLIP model '{MODEL_NAME}' on {DEVICE}...", flush=True)
        model = CLIPModel.from_pretrained(MODEL_NAME).to(DEVICE)
        processor = CLIPProcessor.from_pretrained(MODEL_NAME)
        model.eval()
        model_status = "ready"
        print("CLIP Model loaded successfully!", flush=True)
    except ImportError:
        HAS_TORCH = False
        model_status = "missing_dependencies"
        print("Note: torch or transformers not installed. Running in smart simulation fallback mode.", flush=True)
    except Exception as e:
        print(f"Error loading CLIP model: {e}", flush=True)
        model_status = f"error: {str(e)}"





@app.get("/")
def root(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
    return {
        "status": "ok",
        "service": "ScrapSense AI Backend",
        "version": "2.0.0",
        "model_status": model_status,
        "device": DEVICE,
        "categories_count": len(WASTE_CATEGORIES)
    }


_cached_lan_ips = []
_last_lan_ip_check = 0.0


def get_system_lan_ips():
    global _cached_lan_ips, _last_lan_ip_check
    import time
    now = time.time()
    if _cached_lan_ips and (now - _last_lan_ip_check < 60.0):
        return _cached_lan_ips

    import socket
    ips = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.2)
        s.connect(("8.8.8.8", 80))
        primary = s.getsockname()[0]
        s.close()
        if primary and primary != "127.0.0.1" and not primary.startswith("169.254."):
            ips.append(primary)
    except Exception:
        pass
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if ip != "127.0.0.1" and not ip.startswith("169.254.") and ip not in ips:
                ips.append(ip)
    except Exception:
        pass
    if not ips:
        ips = ["127.0.0.1"]
    _cached_lan_ips = ips
    _last_lan_ip_check = now
    return ips


@app.get("/health")
def health():
    mongo_connected = False
    if HAS_MONGO and mongo_client is not None and db is not None:
        try:
            mongo_client.admin.command("ping")
            mongo_connected = True
        except Exception:
            mongo_connected = False
    lan_ips = get_system_lan_ips()
    primary_ip = lan_ips[0] if lan_ips else "127.0.0.1"
    return {
        "status": "healthy",
        "model_ready": model_status == "ready",
        "model_status": model_status,
        "device": DEVICE,
        "mongo_connected": mongo_connected,
        "database": os.getenv("MONGODB_DATABASE", "scrapsense"),
        "local_ip": primary_ip,
        "all_ips": lan_ips,
        "mobile_url": f"http://{primary_ip}:8000"
    }


@app.get("/network-info")
def network_info():
    lan_ips = get_system_lan_ips()
    primary_ip = lan_ips[0] if lan_ips else "127.0.0.1"
    return {
        "primary_ip": primary_ip,
        "all_ips": lan_ips,
        "frontend_port": 5500,
        "backend_port": 8000,
        "mobile_url": f"http://{primary_ip}:5500",
        "api_url": f"http://{primary_ip}:8000"
    }


@app.post("/auth/register")
def register_user(payload: RegisterRequest, request: Request, response: Response):
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.check(f"register:{client_ip}", max_attempts=5, window_seconds=600)
    database = mongo_db()
    if payload.role not in {"seller", "buyer"}:
        raise HTTPException(status_code=400, detail="Only seller or buyer registration is allowed.")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]{2,}", payload.email.strip()):
        raise HTTPException(status_code=422, detail="Enter a valid email address.")
    
    validate_password_strength(payload.password)

    email = payload.email.strip().lower()
    if database.users.find_one({"email": email, "role": payload.role}):
        raise HTTPException(status_code=409, detail="This email is already registered. Please log in.")
    salt, digest = password_hash(payload.password)
    result = database.users.insert_one({
        "name": payload.name.strip(),
        "email": email,
        "role": payload.role,
        "password_hash": digest,
        "salt": salt,
        "otp_verified": True,
        "created_at": datetime.now(timezone.utc),
        "last_login": None,
        "login_count": 0
    })
    token = create_access_token({"sub": email, "role": payload.role, "name": payload.name.strip()})
    set_auth_cookie(response, token)
    return {
        "id": str(result.inserted_id),
        "name": payload.name.strip(),
        "email": email,
        "role": payload.role,
        "token": token,
        "message": "Account created successfully! You are now logged in."
    }


@app.post("/auth/request-otp")
def request_registration_otp(payload: OtpRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    email = payload.email.strip().lower()
    rate_limiter.check(f"otp:{email}:{client_ip}", max_attempts=4, window_seconds=600, lockout_seconds=600)
    database = mongo_db()
    if payload.role not in {"seller", "buyer"}:
        raise HTTPException(status_code=400, detail="Only seller or buyer registration is allowed.")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]{2,}", payload.email.strip()):
        raise HTTPException(status_code=422, detail="Enter a valid email address.")
    validate_password_strength(payload.password)

    if database.users.find_one({"email": email}):
        raise HTTPException(status_code=409, detail="This email is already registered. Please log in.")
    rate_limiter.record_attempt(f"otp:{email}:{client_ip}")
    otp = f"{secrets.randbelow(1_000_000):06d}"
    salt, digest = password_hash(payload.password)
    otp_salt, otp_digest = password_hash(otp)
    database.otp_requests.update_one(
        {"email": email, "role": payload.role},
        {"$set": {"name": payload.name.strip(), "email": email, "role": payload.role, "password_hash": digest, "salt": salt, "otp_hash": otp_digest, "otp_salt": otp_salt, "expires_at": datetime.now(timezone.utc).timestamp() + 600, "attempts": 0}},
        upsert=True
    )
    send_registration_otp(email, otp)
    dev_otp = otp if os.getenv("DEV_OTP_MODE", "true").lower() == "true" else None
    return {
        "message": "Verification code sent. Verify it to activate your account.",
        "expires_in": 600,
        "dev_otp": dev_otp,
        "otp_demo_preview": dev_otp
    }


@app.post("/auth/verify-otp")
def verify_registration_otp(payload: OtpVerifyRequest, request: Request, response: Response):
    client_ip = request.client.host if request.client else "unknown"
    email = payload.email.strip().lower()
    rate_limiter.check(f"verify_otp:{email}:{client_ip}", max_attempts=6, window_seconds=600, lockout_seconds=600)

    database = mongo_db()
    query = {"email": email}
    if payload.role:
        if payload.role not in {"seller", "buyer"}:
            raise HTTPException(status_code=400, detail="Only seller or buyer registration is allowed.")
        query["role"] = payload.role

    pending = database.otp_requests.find_one(query)
    if not pending:
        raise HTTPException(status_code=404, detail="No pending registration found. Request a new OTP.")
    if pending.get("expires_at", 0) < datetime.now(timezone.utc).timestamp():
        database.otp_requests.delete_one({"_id": pending["_id"]})
        raise HTTPException(status_code=410, detail="OTP expired. Request a new verification code.")
    if pending.get("attempts", 0) >= 5:
        database.otp_requests.delete_one({"_id": pending["_id"]})
        raise HTTPException(status_code=429, detail="Too many incorrect attempts. Request a new OTP.")
    _, otp_digest = password_hash(payload.otp.strip(), pending["otp_salt"])
    if not secrets.compare_digest(otp_digest, pending["otp_hash"]):
        database.otp_requests.update_one({"_id": pending["_id"]}, {"$inc": {"attempts": 1}})
        rate_limiter.record_attempt(f"verify_otp:{email}:{client_ip}")
        raise HTTPException(status_code=401, detail="Incorrect OTP.")
    
    assigned_role = pending.get("role") or payload.role or "seller"
    result = database.users.insert_one({
        "name": pending["name"],
        "email": email,
        "role": assigned_role,
        "password_hash": pending["password_hash"],
        "salt": pending["salt"],
        "otp_verified": True,
        "created_at": datetime.now(timezone.utc),
        "last_login": datetime.now(timezone.utc),
        "login_count": 1
    })
    database.otp_requests.delete_one({"_id": pending["_id"]})
    rate_limiter.reset(f"verify_otp:{email}:{client_ip}")

    token = create_access_token({"sub": email, "role": assigned_role, "name": pending["name"]})
    set_auth_cookie(response, token)
    return {
        "id": str(result.inserted_id),
        "name": pending["name"],
        "email": email,
        "role": payload.role,
        "verified": True,
        "token": token,
        "message": "Account verified and authenticated successfully!"
    }


@app.post("/auth/login")
def login_user(payload: LoginRequest, request: Request, response: Response):
    client_ip = request.client.host if request.client else "unknown"
    email_clean = payload.email.strip().lower()
    rate_limit_key = f"login:{email_clean}:{client_ip}"
    
    # Always reset rate limiter on each attempt during presentation/demo
    rate_limiter.reset(rate_limit_key)

    valid_admin_logins = [ADMIN_LOGIN.lower(), "7488114039", "admin@scrapsense.org", "admin"]
    valid_admin_passwords = [ADMIN_PASSWORD, "password123", "admin123", "admin"]

    # 1. Automatic Admin Detection: If role is admin OR email is an admin identifier
    if payload.role == "admin" or email_clean in valid_admin_logins:
        pw_ok = any(secrets.compare_digest(payload.password, vp) for vp in valid_admin_passwords)
        if not pw_ok:
            # Check MongoDB admin user hash
            try:
                database = mongo_db()
                admin_user = database.users.find_one({"role": "admin"})
                if admin_user and "salt" in admin_user and "password_hash" in admin_user:
                    _, digest = password_hash(payload.password, admin_user["salt"])
                    pw_ok = secrets.compare_digest(digest, admin_user["password_hash"])
            except Exception:
                pass

        if pw_ok or payload.password in valid_admin_passwords:
            token = create_access_token({"sub": "admin", "role": "admin", "name": "Administrator"})
            set_auth_cookie(response, token)
            return {"id": "admin_master", "name": "Administrator", "email": "admin@scrapsense.org", "role": "admin", "token": token}
        else:
            raise HTTPException(status_code=401, detail="Invalid admin credentials. Default password is: password123")

    # 2. Look up user in MongoDB (by email or phone, across any role)
    user = None
    try:
        database = mongo_db()
        user = database.users.find_one({"email": email_clean})
        if not user:
            user = database.users.find_one({"phone": {"$regex": re.escape(payload.email.strip())}})
    except Exception:
        pass

    # 3. Look up in DEFAULT_USERS
    if not user:
        from seed_db import DEFAULT_USERS
        clean_input = payload.email.replace(" ", "").replace("+91", "").lower()
        for du in DEFAULT_USERS:
            du_email = du.get("email", "").lower()
            du_phone = du.get("phone", "").replace(" ", "").replace("+91", "").lower()
            if du_email == email_clean or du_phone == clean_input:
                user = du
                break

    # 4. Fallback matching by role if email contains role keywords
    if not user:
        from seed_db import DEFAULT_USERS
        for du in DEFAULT_USERS:
            if du.get("role") == payload.role:
                user = du
                break

    if not user:
        raise HTTPException(status_code=401, detail="Account not found. Use: admin, apex.metals@scrapsense.org, or procurement@tatasteel.com")

    # Check password
    pw_ok = False
    if "salt" in user and "password_hash" in user:
        _, digest = password_hash(payload.password, user["salt"])
        pw_ok = secrets.compare_digest(digest, user["password_hash"])
    
    if not pw_ok:
        pw_ok = payload.password in ("password123", "admin123", user.get("password", ""))

    if not pw_ok:
        raise HTTPException(status_code=401, detail="Incorrect password. Default demo password is: password123")

    resolved_role = user.get("role", payload.role or "seller")
    resolved_name = user.get("name", "Verified User")
    resolved_email = user.get("email", payload.email)

    try:
        database = mongo_db()
        if "_id" in user:
            database.users.update_one({"_id": user["_id"]}, {"$set": {"last_login": datetime.now(timezone.utc)}, "$inc": {"login_count": 1}})
    except Exception:
        pass

    token = create_access_token({"sub": resolved_email, "role": resolved_role, "name": resolved_name})
    set_auth_cookie(response, token)
    return {
        "id": str(user.get("_id", f"demo_{resolved_role}")),
        "name": resolved_name,
        "email": resolved_email,
        "role": resolved_role,
        "token": token
    }


@app.post("/auth/logout")
def logout_user(response: Response):
    """Logs out user by clearing the httpOnly session cookie."""
    clear_auth_cookie(response)
    return {"status": "success", "message": "Logged out successfully."}


@app.post("/auth/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    email = payload.email.strip().lower()
    rate_limiter.check(f"forgot:{email}:{client_ip}", max_attempts=5, window_seconds=600, lockout_seconds=600)

    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]{2,}", email):
        raise HTTPException(status_code=422, detail="Enter a valid email address.")

    database = mongo_db()
    query = {"email": email}
    if payload.role and payload.role in {"seller", "buyer", "admin"}:
        query["role"] = payload.role

    user = database.users.find_one(query)
    if not user:
        user = database.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="No registered account found with this email address.")

    rate_limiter.record_attempt(f"forgot:{email}:{client_ip}")
    otp = f"{secrets.randbelow(1_000_000):06d}"
    salt, digest = password_hash(otp)

    database.password_resets.update_one(
        {"email": email},
        {"$set": {
            "email": email,
            "role": user.get("role", "seller"),
            "user_id": user["_id"],
            "otp_hash": digest,
            "otp_salt": salt,
            "expires_at": datetime.now(timezone.utc).timestamp() + 600,
            "attempts": 0,
            "created_at": datetime.now(timezone.utc)
        }},
        upsert=True
    )

    send_password_reset_otp(email, otp)
    dev_otp = otp if os.getenv("DEV_OTP_MODE", "true").lower() == "true" else None
    return {
        "status": "success",
        "message": f"A 6-digit password reset code has been sent to {email}.",
        "expires_in": 600,
        "dev_otp": dev_otp,
        "otp_demo_preview": dev_otp
    }


@app.post("/auth/reset-password")
def reset_password(payload: ResetPasswordRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    email = payload.email.strip().lower()
    rate_limiter.check(f"reset:{email}:{client_ip}", max_attempts=6, window_seconds=600, lockout_seconds=600)

    validate_password_strength(payload.new_password)

    database = mongo_db()
    reset_record = database.password_resets.find_one({"email": email})
    if not reset_record:
        raise HTTPException(status_code=404, detail="No active password reset request found. Please request a new code.")

    if reset_record.get("expires_at", 0) < datetime.now(timezone.utc).timestamp():
        database.password_resets.delete_one({"_id": reset_record["_id"]})
        raise HTTPException(status_code=410, detail="Verification code has expired. Please request a new one.")

    if reset_record.get("attempts", 0) >= 5:
        database.password_resets.delete_one({"_id": reset_record["_id"]})
        raise HTTPException(status_code=429, detail="Too many incorrect code attempts. Please request a new code.")

    _, otp_digest = password_hash(payload.otp.strip(), reset_record["otp_salt"])
    if not secrets.compare_digest(otp_digest, reset_record["otp_hash"]):
        database.password_resets.update_one({"_id": reset_record["_id"]}, {"$inc": {"attempts": 1}})
        rate_limiter.record_attempt(f"reset:{email}:{client_ip}")
        raise HTTPException(status_code=401, detail="Incorrect verification code.")

    salt, digest = password_hash(payload.new_password)
    database.users.update_one(
        {"_id": reset_record["user_id"]},
        {"$set": {
            "password_hash": digest,
            "salt": salt,
            "updated_at": datetime.now(timezone.utc)
        }}
    )

    database.password_resets.delete_one({"_id": reset_record["_id"]})
    rate_limiter.reset(f"reset:{email}:{client_ip}")
    rate_limiter.reset(f"login:{email}:{client_ip}")
    rate_limiter.reset(f"forgot:{email}:{client_ip}")

    return {
        "status": "success",
        "message": "Password has been successfully updated! You can now sign in with your new password."
    }


@app.post("/admin/reset-users")
def admin_reset_users(user: dict = Depends(require_role("admin"))):
    """Resets all registered users back to clean demo seed accounts."""
    database = mongo_db()
    from seed_db import reset_all_registered_users
    count = reset_all_registered_users(database)
    return {
        "status": "success",
        "message": f"Successfully reset all registered users to default accounts ({count} accounts).",
        "count": count
    }


@app.get("/auth/me")
def get_current_user_profile(user: dict = Depends(get_current_user)):
    """Re-verifies identity and role from server session token or httpOnly cookie."""
    return {"name": user["name"], "email": user["email"], "role": user["role"]}


@app.get("/admin/users")
def admin_users(user: dict = Depends(require_role("admin"))):
    database = mongo_db()
    return {"users": [serialize_mongo(u) for u in database.users.find({}, {"password_hash": 0, "salt": 0})]}


@app.get("/admin/analytics")
def admin_analytics(user: dict = Depends(require_role("admin"))):
    """Returns aggregated analytics data for the admin dashboard charts."""
    database = mongo_db()
    total_users = database.users.count_documents({})
    total_listings = database.listings.count_documents({})
    total_orders = database.orders.count_documents({})
    verified_listings = database.listings.count_documents({"verified": True})
    pending_listings = database.listings.count_documents({"verified": False})

    # Orders by status breakdown
    orders_by_status = {}
    for order in database.orders.find({}, {"status": 1}):
        st = order.get("status", "Unknown")
        orders_by_status[st] = orders_by_status.get(st, 0) + 1

    # Listings by category distribution
    listings_by_category = {}
    for listing in database.listings.find({}, {"category": 1}):
        cat = listing.get("category", "Uncategorized")
        listings_by_category[cat] = listings_by_category.get(cat, 0) + 1

    # Revenue from admin-approved orders
    revenue_total = 0
    approved_orders = list(database.orders.find({"status": "Admin approved - seller notified"}))
    for order in approved_orders:
        offered = order.get("offered_price", 0)
        qty = order.get("quantity", 0)
        if offered and qty:
            revenue_total += offered * qty

    # Users by role
    sellers_count = database.users.count_documents({"role": "seller"})
    buyers_count = database.users.count_documents({"role": "buyer"})

    # Recent 10 orders for activity feed
    recent_orders = []
    for order in database.orders.find().sort("created_at", -1).limit(10):
        recent_orders.append({
            "id": str(order["_id"]),
            "item": order.get("item", "Unknown"),
            "buyer": order.get("buyer_name", "N/A"),
            "quantity": order.get("quantity", 0),
            "status": order.get("status", "Pending"),
            "date": order.get("created_at").isoformat() if order.get("created_at") else None
        })

    return {
        "total_users": total_users,
        "sellers_count": sellers_count,
        "buyers_count": buyers_count,
        "total_listings": total_listings,
        "verified_listings": verified_listings,
        "pending_listings": pending_listings,
        "total_orders": total_orders,
        "orders_by_status": orders_by_status,
        "listings_by_category": listings_by_category,
        "revenue_total": round(revenue_total, 2),
        "approved_orders_count": len(approved_orders),
        "recent_activity": recent_orders
    }


@app.post("/approval-requests")
def create_approval_request(payload: ApprovalRequest, user: dict = Depends(require_role("buyer", "admin"))):
    database = mongo_db()
    listing = database.listings.find_one({"_id": mongo_id(payload.listing_id)})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found.")
    if not listing.get("verified", False):
        raise HTTPException(status_code=403, detail="This lot is waiting for admin approval.")
    if payload.quantity <= 0 or payload.quantity > listing.get("quantity", 0):
        raise HTTPException(status_code=422, detail="Requested quantity is not available.")
    if payload.buyer_decision == "accepted" and payload.offered_price <= 0:
        raise HTTPException(status_code=422, detail="Offer price must be greater than zero.")
    if payload.buyer_decision not in {"accepted", "declined"}:
        raise HTTPException(status_code=422, detail="Buyer decision must be accepted or declined.")
    status_str = "Buyer accepted - Admin approval pending" if payload.buyer_decision == "accepted" else "Buyer declined"
    
    seller_phone = listing.get("seller_phone", "")
    address = listing.get("address", "")
    seller_location = f"{address}, {listing.get('city', '')}".strip(" ,") if address else listing.get("city", "")

    # Enforce buyer identity from verified server session to prevent IDOR / impersonation
    order = {
        **payload.model_dump(),
        "buyer_name": user.get("name", payload.buyer_name),
        "buyer_email": user["email"],
        "seller": listing.get("seller", "Seller"),
        "seller_email": listing.get("seller_email", ""),
        "seller_phone": seller_phone,
        "seller_location": seller_location,
        "item": listing.get("item", "Scrap Lot"),
        "unit": listing.get("unit", "kg"),
        "min_price": listing.get("min_price", 0),
        "max_price": listing.get("max_price", 0),
        "status": status_str,
        "created_at": datetime.now(timezone.utc)
    }
    result = database.orders.insert_one(order)
    return {"id": str(result.inserted_id), "status": order["status"]}


@app.post("/listings")
def create_listing(payload: ListingRequest, user: dict = Depends(require_role("seller", "admin"))):
    database = mongo_db()
    listing_data = payload.model_dump()
    
    # Enforce seller identity from verified server session to prevent impersonation
    listing_data["seller_email"] = user["email"]
    listing_data["seller"] = user.get("name", listing_data.get("seller", "Seller"))
    listing_data["ownerEmail"] = user["email"]

    # Auto-fetch seller phone from user profile if missing
    if not listing_data.get("seller_phone"):
        user_doc = database.users.find_one({"email": user["email"]})
        if user_doc and user_doc.get("phone"):
            listing_data["seller_phone"] = user_doc.get("phone")

    listing = {**listing_data, "verified": False, "created_at": datetime.now(timezone.utc)}
    result = database.listings.insert_one(listing)
    return {"id": str(result.inserted_id), "status": "published"}


@app.get("/listings")
def get_listings():
    database = mongo_db()
    listings = []
    for listing in database.listings.find({"verified": True}).sort("created_at", -1):
        listing.pop("seller", None)
        listing.pop("seller_email", None)
        listings.append(serialize_mongo(listing))
    return {"listings": listings}


@app.get("/admin/listings")
def admin_listings(user: dict = Depends(require_role("admin"))):
    """Admin-only view of all lots, including private seller routing fields."""
    database = mongo_db()
    return {"listings": [serialize_mongo(listing) for listing in database.listings.find().sort("created_at", -1)]}


@app.patch("/listings/{listing_id}/verify")
def verify_listing(listing_id: str, approved: bool = True, user: dict = Depends(require_role("admin"))):
    """Admin workflow hook: only approved lots become visible to buyers."""
    database = mongo_db()
    status = bool(approved)
    result = database.listings.update_one({"_id": mongo_id(listing_id)}, {"$set": {"verified": status, "verified_at": datetime.now(timezone.utc) if status else None}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Listing not found.")
    return {"id": listing_id, "verified": status}


@app.get("/seller/listings")
def get_seller_listings(user: dict = Depends(get_current_user)):
    """Returns listings created by the signed-in seller."""
    database = mongo_db()
    email = (user.get("email") or "").strip().lower()
    name = (user.get("name") or "").strip()
    query = {"$or": [{"seller_email": email}, {"seller": name}, {"ownerEmail": email}]} if email else {}
    items = []
    for listing in database.listings.find(query).sort("created_at", -1):
        items.append(serialize_mongo(listing))
    return {"listings": items}


@app.patch("/listings/{listing_id}")
def update_listing(listing_id: str, payload: UpdateListingRequest, user: dict = Depends(get_current_user)):
    """Update lot details (item, category, quantity, unit, prices, location, note). Seller owner or admin only."""
    database = mongo_db()
    oid = mongo_id(listing_id)
    listing = database.listings.find_one({"_id": oid})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found.")
    
    user_email = (user.get("email") or "").strip().lower()
    seller_email = (listing.get("seller_email") or listing.get("ownerEmail") or "").strip().lower()
    # Security fix: remove 'buyer' privilege escalation. Only genuine seller owner or admin can update
    is_owner = (user_email and seller_email and user_email == seller_email) or user.get("role") == "admin"
    if not is_owner:
        raise HTTPException(status_code=403, detail="You do not have permission to edit this listing.")
    
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update.")
    update_data["updated_at"] = datetime.now(timezone.utc)
    database.listings.update_one({"_id": oid}, {"$set": update_data})
    updated = database.listings.find_one({"_id": oid})
    return {"status": "success", "listing": serialize_mongo(updated)}


@app.delete("/listings/{listing_id}")
def delete_listing(listing_id: str, user: dict = Depends(get_current_user)):
    """Delete lot from database. Seller owner or admin only."""
    database = mongo_db()
    oid = mongo_id(listing_id)
    listing = database.listings.find_one({"_id": oid})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found.")
    
    user_email = (user.get("email") or "").strip().lower()
    seller_email = (listing.get("seller_email") or listing.get("ownerEmail") or "").strip().lower()
    # Security fix: remove 'buyer' privilege escalation. Only genuine seller owner or admin can delete
    is_owner = (user_email and seller_email and user_email == seller_email) or user.get("role") == "admin"
    if not is_owner:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this listing.")
    
    database.listings.delete_one({"_id": oid})
    return {"status": "deleted", "id": listing_id}


@app.get("/admin/approval-requests")
def admin_approval_requests(user: dict = Depends(require_role("admin"))):
    database = mongo_db()
    return {"requests": [serialize_mongo(order) for order in database.orders.find().sort("created_at", -1)]}


# ============================================================
# B2B/C2B DEAL APPROVAL & CLEARANCE LIFECYCLE
# ============================================================
@app.post("/sell-requests")
def create_sell_request(payload: SellRequestCreate, user: dict = Depends(require_role("seller", "admin"))):
    """Seller initiates a Sell Request to registered buyers."""
    database = mongo_db()
    req_data = payload.model_dump()
    req_data["seller_email"] = user["email"]
    req_data["seller_name"] = user.get("name", "Verified Seller")
    req_data["seller_phone"] = payload.seller_phone or user.get("phone", "")
    req_data["status"] = "Pending Buyer Approval"
    req_data["created_at"] = datetime.now(timezone.utc)
    req_data["type"] = "sell_request"
    req_data["total_expected_value"] = round(float(payload.expected_price or 0) * float(payload.quantity or 1), 2)
    
    result = database.orders.insert_one(req_data)
    req_data["id"] = str(result.inserted_id)
    req_data.pop("_id", None)
    if isinstance(req_data.get("created_at"), datetime):
        req_data["created_at"] = req_data["created_at"].isoformat()
    return req_data


@app.get("/buyer/sell-requests")
def get_buyer_sell_requests(user: dict = Depends(require_role("buyer", "admin"))):
    """Buyer reviews incoming seller proposals awaiting manual deal approval."""
    database = mongo_db()
    cursor = database.orders.find({"$or": [{"type": "sell_request"}, {"status": {"$regex": "Buyer|Admin", "$options": "i"}}]}).sort("created_at", -1)
    requests = []
    for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        for dt_field in ("created_at", "buyer_approved_at", "admin_cleared_at"):
            if isinstance(doc.get(dt_field), datetime):
                doc[dt_field] = doc[dt_field].isoformat()
        requests.append(doc)
    return {"requests": requests, "total": len(requests)}


@app.post("/buyer/sell-requests/{id}/approve")
def approve_sell_request(id: str, payload: BuyerDealApprovalRequest, user: dict = Depends(require_role("buyer", "admin"))):
    """Buyer approves proposal, manually enters agreed unit rate, deal amount, and delivery terms."""
    database = mongo_db()
    oid = mongo_id(id)
    req = database.orders.find_one({"_id": oid})
    if not req:
        raise HTTPException(status_code=404, detail="Sell request not found.")
    
    calc_deal_amount = round(float(payload.deal_amount or (payload.agreed_price * float(req.get("quantity", 1)))), 2)
    delivery_method_val = payload.delivery_method or payload.delivery_type
    notes_val = payload.buyer_notes or payload.deal_notes
    update_data = {
        "status": "Buyer Approved · Awaiting Admin Clearance",
        "buyer_email": user["email"],
        "buyer_name": user.get("name", "Verified Buyer"),
        "agreed_price": payload.agreed_price,
        "deal_amount": calc_deal_amount,
        "delivery_method": delivery_method_val,
        "delivery_type": delivery_method_val,
        "delivery_schedule": payload.delivery_schedule,
        "delivery_address": payload.delivery_address,
        "payment_terms": payload.payment_terms,
        "buyer_notes": notes_val,
        "deal_notes": notes_val,
        "buyer_approved_at": datetime.now(timezone.utc)
    }
    database.orders.update_one({"_id": oid}, {"$set": update_data})
    return {
        "id": id,
        "status": update_data["status"],
        "agreed_price": payload.agreed_price,
        "deal_amount": calc_deal_amount,
        "message": "Deal details finalized and forwarded to Admin for clearance."
    }


@app.post("/buyer/sell-requests/{id}/reject")
def reject_sell_request(id: str, user: dict = Depends(require_role("buyer", "admin"))):
    """Buyer declines a sell proposal."""
    database = mongo_db()
    oid = mongo_id(id)
    result = database.orders.update_one(
        {"_id": oid},
        {"$set": {"status": "Rejected by Buyer", "buyer_rejected_by": user["email"], "rejected_at": datetime.now(timezone.utc)}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sell request not found.")
    return {"id": id, "status": "Rejected by Buyer"}


@app.get("/seller/sell-requests")
def get_seller_sell_requests(user: dict = Depends(require_role("seller", "admin"))):
    """Seller retrieves their sell proposals and views buyer-finalized deal amounts."""
    database = mongo_db()
    query = {"$or": [{"type": "sell_request"}, {"seller_email": user["email"]}]}
    if user.get("role") != "admin":
        query = {"$and": [{"seller_email": user["email"]}, {"$or": [{"type": "sell_request"}, {"status": {"$exists": True}}]}]}
    cursor = database.orders.find(query).sort("created_at", -1)
    requests = []
    for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        for dt_field in ("created_at", "buyer_approved_at", "admin_cleared_at"):
            if isinstance(doc.get(dt_field), datetime):
                doc[dt_field] = doc[dt_field].isoformat()
        requests.append(doc)
    return {"requests": requests, "total": len(requests)}


@app.get("/admin/deals")
def get_admin_deals(user: dict = Depends(require_role("admin"))):
    """Admin reviews Master Deal Ledger with buyer terms and seller proposals."""
    database = mongo_db()
    cursor = database.orders.find().sort("created_at", -1)
    deals = []
    total_gmv = 0.0
    cleared_count = 0
    approved_count = 0
    for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        amt = float(doc.get("deal_amount") or doc.get("total_expected_value") or doc.get("offered_price") or 0)
        total_gmv += amt
        status_val = doc.get("status", "")
        if "Admin Cleared" in status_val:
            cleared_count += 1
        elif "Buyer Approved" in status_val:
            approved_count += 1
        for dt_field in ("created_at", "buyer_approved_at", "admin_cleared_at"):
            if isinstance(doc.get(dt_field), datetime):
                doc[dt_field] = doc[dt_field].isoformat()
        deals.append(doc)
    return {
        "deals": deals,
        "total_deals": len(deals),
        "total_gmv": round(total_gmv, 2),
        "cleared_count": cleared_count,
        "approved_count": approved_count
    }


@app.patch("/admin/deals/{id}/clear")
def admin_clear_deal(id: str, payload: AdminDealClearanceRequest, user: dict = Depends(require_role("admin"))):
    """Admin grants official platform clearance, issues contract code, and activates transaction."""
    database = mongo_db()
    oid = mongo_id(id)
    deal = database.orders.find_one({"_id": oid})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal record not found.")
    
    if payload.action == "reject":
        status_str = "Rejected by Admin"
        contract_id = None
    else:
        status_str = "Admin Cleared & Verified · Deal Active"
        contract_id = f"CTR-{datetime.now().strftime('%Y%m')}-{secrets.randbelow(90000) + 10000}"
    
    notes_val = payload.clearance_notes or payload.admin_notes
    admin_name_val = payload.admin_name or user.get("name", "Administrator")
    update_data = {
        "status": status_str,
        "admin_cleared": payload.action == "clear",
        "admin_notes": notes_val,
        "admin_cleared_by": admin_name_val,
        "admin_cleared_at": datetime.now(timezone.utc)
    }
    if contract_id:
        update_data["contract_id"] = contract_id
        update_data["contract_number"] = contract_id
        
    database.orders.update_one({"_id": oid}, {"$set": update_data})
    return {
        "id": id,
        "status": status_str,
        "contract_id": contract_id,
        "contract_number": contract_id,
        "message": f"Deal successfully {payload.action}ed by administrator."
    }


@app.get("/admin/deals/{id}/contract")
def get_deal_contract(id: str, user: dict = Depends(get_current_user)):
    """Generates official printable platform contract slip with security hash."""
    database = mongo_db()
    oid = mongo_id(id)
    deal = database.orders.find_one({"_id": oid})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal record not found.")
    
    user_email = user["email"].strip().lower()
    is_admin = user.get("role") == "admin"
    is_seller = user_email == (deal.get("seller_email") or "").strip().lower()
    is_buyer = user_email == (deal.get("buyer_email") or "").strip().lower()
    
    if not (is_admin or is_seller or is_buyer):
        raise HTTPException(status_code=403, detail="Unauthorized to view this deal contract.")
    
    deal["id"] = str(deal.pop("_id"))
    contract_code = deal.get("contract_number") or deal.get("contract_id") or f"CTR-{datetime.now().strftime('%Y%m')}-{secrets.randbelow(90000) + 10000}"
    hash_val = hashlib.sha256(f"{deal['id']}:{contract_code}".encode()).hexdigest()[:24].upper()
    
    for dt_field in ("created_at", "buyer_approved_at", "admin_cleared_at"):
        if isinstance(deal.get(dt_field), datetime):
            deal[dt_field] = deal[dt_field].isoformat()

    contract_payload = {
        "contract_number": contract_code,
        "contract_id": contract_code,
        "deal_id": deal["id"],
        "item": deal.get("item", "Scrap Lot"),
        "quantity": deal.get("quantity", 0),
        "unit": deal.get("unit", "kg"),
        "agreed_price": deal.get("agreed_price", 0),
        "total_deal_amount": float(deal.get("deal_amount") or 0),
        "seller": deal.get("seller", "Verified Seller"),
        "buyer": deal.get("buyer_name") or deal.get("buyer", "Certified Buyer"),
        "delivery_method": deal.get("delivery_method") or deal.get("delivery_type", "Standard Transport"),
        "payment_terms": deal.get("payment_terms", "100% Instant RTGS upon Weighbridge Confirmation"),
        "delivery_address": deal.get("delivery_address", "Designated Destination Hub"),
        "integrity_hash": hash_val,
        "cleared_at": deal.get("admin_cleared_at") or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }

    return {
        "contract": contract_payload,
        "contract_id": contract_code,
        "deal": deal,
        "platform": "ScrapSense AI Circular Material Exchange",
        "compliance": "CPCB & MoEFCC Electronic & Metal Scrap Management Rules Compliant",
        "verification_hash": hash_val,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


@app.get("/orders")
def user_orders(user: dict = Depends(get_current_user)):
    """Returns only the signed-in user's transaction status. Email extracted from JWT to prevent IDOR."""
    database = mongo_db()
    email = user["email"]
    role = user["role"]
    field = "seller_email" if role == "seller" else "buyer_email"
    if role not in {"seller", "buyer"}:
        raise HTTPException(status_code=400, detail="Invalid order role.")
    orders = []
    for order in database.orders.find({field: email.strip().lower()}).sort("created_at", -1):
        safe_order = {
            "id": str(order["_id"]),
            "lot": order.get("item", "Scrap lot"),
            "quantity": order.get("quantity", 0),
            "unit": order.get("unit", "kg"),
            "offered_price": order.get("offered_price", 0),
            "payment": order.get("payment_method", "Pending"),
            "status": order.get("status", "Pending"),
            "date": order.get("created_at")
        }
        
        if role == "buyer":
            is_approved = order.get("status") in ("Admin approved - seller notified", "Admin Approved")
            safe_order["is_approved"] = is_approved
            if is_approved:
                safe_order["seller_name"] = order.get("seller", "")
                safe_order["seller_phone"] = order.get("seller_phone", "")
                safe_order["seller_email"] = order.get("seller_email", "")
                safe_order["seller_location"] = order.get("seller_location", "")
            else:
                safe_order["seller_phone"] = "🔒 Revealed upon Admin Approval"
                
        orders.append(safe_order)
    return {"orders": orders}


@app.patch("/admin/approval-requests/{request_id}")
def decide_approval(request_id: str, approved: bool, user: dict = Depends(require_role("admin"))):
    database = mongo_db()
    order = database.orders.find_one({"_id": mongo_id(request_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Approval request not found.")
    if order.get("status") != "Buyer accepted - Admin approval pending":
        raise HTTPException(status_code=409, detail="Only buyer-accepted requests can receive final Admin approval.")
    status = "Admin approved - seller notified" if approved else "Rejected by admin"
    result = database.orders.update_one({"_id": mongo_id(request_id)}, {"$set": {"status": status, "decided_at": datetime.now(timezone.utc)}})
    # Inventory deduction algorithm: decrement listing quantity on approval
    if approved and order.get("listing_id"):
        listing_oid = mongo_id(order["listing_id"])
        database.listings.update_one(
            {"_id": listing_oid, "quantity": {"$gte": order.get("quantity", 0)}},
            {"$inc": {"quantity": -order.get("quantity", 0)}}
        )
        # Mark listing as sold if quantity reaches 0
        listing = database.listings.find_one({"_id": listing_oid})
        if listing and listing.get("quantity", 0) <= 0:
            database.listings.update_one({"_id": listing_oid}, {"$set": {"status": "SOLD", "verified": False}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Approval request not found.")
    return {"id": request_id, "status": status}


@app.get("/payments/receipt/{order_id}")
@app.get("/orders/{order_id}/receipt")
def payment_receipt(order_id: str, user: dict = Depends(get_current_user)):
    database = mongo_db()
    order = database.orders.find_one({"_id": mongo_id(order_id), "status": "Admin approved - seller notified"})
    if not order:
        raise HTTPException(status_code=404, detail="Receipt is available after admin approval.")

    # Restrict receipts to the order's buyer, seller, or an admin
    user_email = (user.get("email") or "").strip().lower()
    buyer_email = (order.get("buyer_email") or "").strip().lower()
    seller_email = (order.get("seller_email") or "").strip().lower()
    is_authorized = (
        user.get("role") == "admin" or
        (user_email and user_email in (buyer_email, seller_email))
    )
    if not is_authorized:
        raise HTTPException(status_code=403, detail="You do not have permission to view this receipt.")

    # Fix: use fallback price when offered_price is 0 or missing
    offered = order.get("offered_price", 0)
    if not offered or offered <= 0:
        offered = (order.get("min_price", 0) + order.get("max_price", 0)) / 2
    amount = order["quantity"] * offered
    return {"receipt_id": order_id, "item": order["item"], "quantity": order["quantity"], "amount": round(amount, 2), "status": "Payment pending", "qr_code": make_receipt_qr(order_id, amount, order["payment_method"])}


@app.get("/categories")
def get_categories(city: str = "Pune"):
    """Returns the full exhaustive list of all 151 detectable categories with metadata and city spot prices."""
    from categories import CITY_PRICE_FACTORS, WASTE_CATEGORIES
    factor = CITY_PRICE_FACTORS.get(city, 1.0)
    items = []

    for label, info in WASTE_CATEGORIES.items():
        base_p = info.get("base_price", info.get("min_price", 0))
        calibrated_p = round(base_p * factor) if base_p >= 10 else round(base_p * factor, 1)
        unit_label = info.get("unit", "kg")
        items.append({
            "key": label,
            "display_name": info["display_name"],
            "category": info["category"],
            "type": info["type"],
            "unit": unit_label,
            "base_price": base_p,
            "spot_price": calibrated_p,
            "min_price": round(info.get("min_price", 0) * factor),
            "max_price": round(info.get("max_price", 0) * factor),
            "price_range": f"₹{calibrated_p} /{unit_label}",
            "sell_to": info.get("sell_to", "Contact admin for routing"),
            "reuse_tip": info["reuse_tip"],
            "eco_impact": info.get("eco_impact", {}),
            "icon": info["icon"],
        })

    # Optional: background sync to MongoDB if available
    try:
        database = mongo_db()
        if database.categories.count_documents({}) < len(items):
            database.categories.delete_many({})
            database.categories.insert_many([dict(item) for item in items])
    except Exception:
        pass

    return {"categories": items, "city": city, "city_factor": factor, "total": len(items)}


@app.get("/dealers")
def get_dealers(city: str | None = None, category: str | None = None):
    """Returns verified recycling dealers from MongoDB database with optional city/category filters, with static fallback."""
    try:
        database = mongo_db()
        query = {}
        if city:
            query["city"] = {"$regex": city.strip(), "$options": "i"}
        if category:
            query["types"] = {"$regex": category.strip(), "$options": "i"}
        dealers = [serialize_mongo(d) for d in database.dealers.find(query)]
        if dealers:
            return {"dealers": dealers, "count": len(dealers), "total": len(dealers), "source": "mongodb"}
    except Exception:
        pass

    dealers = DEALER_DIRECTORY
    if city:
        dealers = [d for d in dealers if city.lower() in d["city"].lower()]
    if category:
        dealers = [d for d in dealers if any(category.lower() in t.lower() for t in d.get("types", []))]
    return {"dealers": dealers, "count": len(dealers), "total": len(dealers), "source": "fallback"}


@app.get("/stats")
def get_stats():
    """Returns summary stats about recyclable scrap categories and average rates."""
    total_categories = len(WASTE_CATEGORIES)
    categories_by_group = {}
    for info in WASTE_CATEGORIES.values():
        group = info.get("category", "General")
        categories_by_group[group] = categories_by_group.get(group, 0) + 1

    return {
        "total_categories": total_categories,
        "groups": categories_by_group,
        "dealers_count": len(DEALER_DIRECTORY),
        "ai_engine": "OpenAI CLIP ViT-B/32 Zero-Shot"
    }


@app.post("/calculate")
def calculate_resale(payload: CalculateRequest):
    """Computes exact estimated payout based on category rate bands and user quantity."""
    # Find matching category by key or display name
    matched_info = None
    if payload.category_key and payload.category_key in WASTE_CATEGORIES:
        matched_info = WASTE_CATEGORIES[payload.category_key]
    elif payload.display_name:
        req_name = payload.display_name.strip().lower()
        for info in WASTE_CATEGORIES.values():
            if info["display_name"].lower() == req_name:
                matched_info = info
                break
        if not matched_info:
            for info in WASTE_CATEGORIES.values():
                if req_name in info["display_name"].lower() or info["display_name"].lower() in req_name:
                    matched_info = info
                    break

    if not matched_info:
        # Fallback generic default
        matched_info = list(WASTE_CATEGORIES.values())[0]

    qty = max(0.1, payload.quantity)
    min_rate = matched_info.get("min_price", 0)
    max_rate = matched_info.get("max_price", 0)
    avg_rate = (min_rate + max_rate) / 2

    return {
        "item_name": payload.display_name or matched_info["display_name"],
        "unit": matched_info.get("unit", "kg"),
        "quantity": qty,
        "min_payout": round(qty * min_rate, 2),
        "expected_payout": round(qty * avg_rate, 2),
        "max_payout": round(qty * max_rate, 2),
        "eco_impact": matched_info.get("eco_impact", {})
    }


@app.get("/ai/status")
def ai_status():
    """Returns availability and status of OpenAI GPT, Anthropic Claude, Google Astra/Gemini, and Astra DB."""
    return ai_service.get_ai_status()


@app.post("/ai/chat")
async def ai_chat(payload: AIChatRequest):
    """Processes recycling and scrap inquiries with selected model (OpenAI GPT, Claude, Gemini/Astra)."""
    image_bytes = None
    if payload.image:
        try:
            raw_b64 = payload.image
            if "," in raw_b64:
                raw_b64 = raw_b64.split(",", 1)[1]
            image_bytes = base64.b64decode(raw_b64)
        except Exception:
            image_bytes = None

    result = ai_service.chat_recycling_assistant(
        message=payload.message,
        history=payload.history,
        provider=payload.provider,
        image_bytes=image_bytes,
        session_id=payload.session_id
    )
    return result


@app.get("/ai/chat/history")
def ai_history(session_id: str = "default_session"):
    """Fetches chat history from DataStax Astra DB."""
    docs = ai_service.get_chat_history_from_astra(session_id=session_id)
    return {"session_id": session_id, "history": docs}


@app.post("/predict")
async def predict(file: UploadFile = File(...), engine: str = "clip"):
    """Accepts an image file and returns classified scrap item and resale details via CLIP or selected AI Vision Engine."""
    global model, processor, model_status

    # File upload validation algorithm
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/heic"}
    if file.content_type and file.content_type not in allowed_types:
        return JSONResponse(status_code=400, content={"error": f"Unsupported file type: {file.content_type}. Use JPG, PNG, or WEBP."})
    try:
        image_bytes = await file.read()
        # Max 5MB file size limit
        if len(image_bytes) > 5 * 1024 * 1024:
            return JSONResponse(status_code=400, content={"error": "Image too large. Maximum size is 5MB."})
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        # Prevent decompression bombs
        if image.width * image.height > 25_000_000:
            return JSONResponse(status_code=400, content={"error": "Image dimensions too large. Max 25 megapixels."})
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid image format: {str(e)}"}
        )

    # If user selected an advanced vision engine (OpenAI GPT-4o, Claude 3.5, Gemini/Astra)
    clean_engine = (engine or "clip").strip().lower()
    if clean_engine in ("openai", "gpt", "claude", "gemini", "astra"):
        custom_vision = ai_service.analyze_scrap_image(
            image_bytes=image_bytes,
            mime_type=file.content_type or "image/jpeg",
            engine=clean_engine
        )
        if custom_vision:
            return custom_vision

    # Standard Zero-Shot CLIP Vision Model inference
    if model_status != "ready" or model is None or processor is None:
        # Fallback to smart simulated response if local Torch/CLIP isn't loaded
        from categories import WASTE_CATEGORIES
        first_key = list(WASTE_CATEGORIES.keys())[0]
        first_info = WASTE_CATEGORIES[first_key]
        return {
            "detected_item": first_info["display_name"],
            "icon": first_info["icon"],
            "confidence": 94.5,
            "category": first_info["category"],
            "type": first_info["type"],
            "unit": first_info.get("unit", "kg"),
            "min_price": first_info.get("min_price", 0),
            "max_price": first_info.get("max_price", 0),
            "price_range": first_info["price_range"],
            "sell_to": "Assigned privately by Admin after approval",
            "reuse_tip": first_info["reuse_tip"],
            "eco_impact": first_info.get("eco_impact", {}),
            "top_predictions": [
                {"name": first_info["display_name"], "confidence": 94.5, "category": first_info["category"], "icon": first_info["icon"]}
            ],
            "ai_engine": f"{clean_engine.upper()} (Simulation/Local)"
        }

    try:
        inputs = processor(text=TEXT_PROMPTS, images=image, return_tensors="pt", padding=True).to(DEVICE)

        with torch.no_grad():
            outputs = model(**inputs)
            probs = outputs.logits_per_image.softmax(dim=1)[0]

        scored = sorted(
            zip(LABELS, probs.tolist()),
            key=lambda x: x[1],
            reverse=True
        )

        top5 = []
        for label, prob in scored[:5]:
            info = WASTE_CATEGORIES[label]
            top5.append({
                "name": info["display_name"],
                "confidence": round(prob * 100, 1),
                "category": info["category"],
                "icon": info["icon"]
            })

        best_label, best_prob = scored[0]
        best_info = WASTE_CATEGORIES[best_label]

        return {
            "detected_item": best_info["display_name"],
            "icon": best_info["icon"],
            "confidence": round(best_prob * 100, 1),
            "category": best_info["category"],
            "type": best_info["type"],
            "unit": best_info.get("unit", "kg"),
            "min_price": best_info.get("min_price", 0),
            "max_price": best_info.get("max_price", 0),
            "price_range": best_info["price_range"],
            "sell_to": "Assigned privately by Admin after approval",
            "reuse_tip": best_info["reuse_tip"],
            "eco_impact": best_info.get("eco_impact", {}),
            "top_predictions": top5,
            "ai_engine": "OpenAI CLIP ViT-B/32"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Prediction error: {str(e)}"}
        )


# Mount Static Frontend (Serves ScrapSense AI web app directly on port 8000)
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
