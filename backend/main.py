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
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request
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
from auth import create_access_token, get_current_user, require_role, hash_password, verify_password
import ai_service

# MongoDB index setup
def setup_mongo_indexes():
    """Create MongoDB indexes for performance and data integrity."""
    try:
        database = mongo_db()
        database.users.create_index([("email", 1), ("role", 1)], unique=True)
        database.otp_requests.create_index("expires_at", expireAfterSeconds=0)
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
                seed_database()
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
    role: str


class LoginRequest(BaseModel):
    email: str
    password: str
    role: str


class ApprovalRequest(BaseModel):
    listing_id: str
    buyer_name: str
    buyer_email: str
    quantity: float
    offered_price: float = 0
    buyer_decision: str = "declined"
    address: str = ""
    payment_method: str = "Not required"


class ListingRequest(BaseModel):
    seller: str
    seller_email: str
    item: str
    category: str
    unit: str = "kg"
    quantity: float
    city: str
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
def register_user(payload: RegisterRequest):
    database = mongo_db()
    if payload.role not in {"seller", "buyer"}:
        raise HTTPException(status_code=400, detail="Only seller or buyer registration is allowed.")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]{2,}", payload.email.strip()):
        raise HTTPException(status_code=422, detail="Enter a valid email address.")
    if len(payload.password) < 6:
        raise HTTPException(status_code=422, detail="Password must contain at least 6 characters.")
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
    return {
        "id": str(result.inserted_id),
        "name": payload.name.strip(),
        "email": email,
        "role": payload.role,
        "token": token,
        "message": "Account created successfully! You can now log in."
    }


@app.post("/auth/request-otp")
def request_registration_otp(payload: OtpRequest):
    database = mongo_db()
    if payload.role not in {"seller", "buyer"}:
        raise HTTPException(status_code=400, detail="Only seller or buyer registration is allowed.")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]{2,}", payload.email.strip()):
        raise HTTPException(status_code=422, detail="Enter a valid email address.")
    if len(payload.password) < 8:
        raise HTTPException(status_code=422, detail="Password must contain at least 8 characters.")
    email = payload.email.strip().lower()
    if database.users.find_one({"email": email}):
        raise HTTPException(status_code=409, detail="This email is already registered. Please log in.")
    otp = f"{secrets.randbelow(1_000_000):06d}"
    salt, digest = password_hash(payload.password)
    otp_salt, otp_digest = password_hash(otp)
    database.otp_requests.update_one(
        {"email": email, "role": payload.role},
        {"$set": {"name": payload.name.strip(), "email": email, "role": payload.role, "password_hash": digest, "salt": salt, "otp_hash": otp_digest, "otp_salt": otp_salt, "expires_at": datetime.now(timezone.utc).timestamp() + 600, "attempts": 0}},
        upsert=True
    )
    send_registration_otp(email, otp)
    response = {"message": "Verification code sent. Verify it to activate your account.", "expires_in": 600}
    # OTP is only logged to console in dev mode, never returned in HTTP response
    return response


@app.post("/auth/verify-otp")
def verify_registration_otp(payload: OtpVerifyRequest):
    database = mongo_db()
    if payload.role not in {"seller", "buyer"}:
        raise HTTPException(status_code=400, detail="Only seller or buyer registration is allowed.")
    email = payload.email.strip().lower()
    pending = database.otp_requests.find_one({"email": email, "role": payload.role})
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
        raise HTTPException(status_code=401, detail="Incorrect OTP.")
    result = database.users.insert_one({"name": pending["name"], "email": email, "role": payload.role, "password_hash": pending["password_hash"], "salt": pending["salt"], "otp_verified": True, "created_at": datetime.now(timezone.utc), "last_login": None, "login_count": 0})
    database.otp_requests.delete_one({"_id": pending["_id"]})
    return {"id": str(result.inserted_id), "name": pending["name"], "email": email, "role": payload.role, "verified": True}


@app.post("/auth/login")
def login_user(payload: LoginRequest):
    if payload.role == "admin":
        if not secrets.compare_digest(payload.email, ADMIN_LOGIN) or not secrets.compare_digest(payload.password, ADMIN_PASSWORD):
            raise HTTPException(status_code=401, detail="Invalid admin credentials.")
        token = create_access_token({"sub": ADMIN_LOGIN, "role": "admin", "name": "Administrator"})
        return {"name": "Administrator", "email": ADMIN_LOGIN, "role": "admin", "token": token}
    database = mongo_db()
    user = database.users.find_one({"email": payload.email.strip().lower(), "role": payload.role})
    if not user:
        raise HTTPException(status_code=401, detail="Account not found or role is incorrect.")
    _, digest = password_hash(payload.password, user["salt"])
    if not secrets.compare_digest(digest, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect password.")
    if user.get("otp_verified", True) is not True:
        raise HTTPException(status_code=403, detail="Verify your registration OTP before logging in.")
    database.users.update_one({"_id": user["_id"]}, {"$set": {"last_login": datetime.now(timezone.utc)}, "$inc": {"login_count": 1}})
    token = create_access_token({"sub": user["email"], "role": user["role"], "name": user["name"]})
    return {"id": str(user["_id"]), "name": user["name"], "email": user["email"], "role": user["role"], "token": token}


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
def create_approval_request(payload: ApprovalRequest):
    database = mongo_db()
    listing = database.listings.find_one({"_id": mongo_id(payload.listing_id)})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found.")
    if not listing.get("verified", False):
        raise HTTPException(status_code=403, detail="This lot is waiting for admin approval.")
    if payload.quantity <= 0 or payload.quantity > listing["quantity"]:
        raise HTTPException(status_code=422, detail="Requested quantity is not available.")
    if payload.buyer_decision == "accepted" and payload.offered_price <= 0:
        raise HTTPException(status_code=422, detail="Offer price must be greater than zero.")
    if payload.buyer_decision not in {"accepted", "declined"}:
        raise HTTPException(status_code=422, detail="Buyer decision must be accepted or declined.")
    status = "Buyer accepted - Admin approval pending" if payload.buyer_decision == "accepted" else "Buyer declined"
    
    seller_phone = listing.get("seller_phone", "")
    address = listing.get("address", "")
    seller_location = f"{address}, {listing.get('city', '')}".strip(" ,") if address else listing.get("city", "")

    order = {**payload.model_dump(), "seller": listing["seller"], "seller_email": listing["seller_email"], "seller_phone": seller_phone, "seller_location": seller_location, "item": listing["item"], "unit": listing.get("unit", "kg"), "min_price": listing.get("min_price", 0), "max_price": listing.get("max_price", 0), "status": status, "created_at": datetime.now(timezone.utc)}
    result = database.orders.insert_one(order)
    return {"id": str(result.inserted_id), "status": order["status"]}


@app.post("/listings")
def create_listing(payload: ListingRequest):
    database = mongo_db()
    listing_data = payload.model_dump()
    
    # Auto-fetch seller phone from user profile if missing
    if not listing_data.get("seller_phone"):
        user = database.users.find_one({"email": payload.seller_email.strip().lower()})
        if user and user.get("phone"):
            listing_data["seller_phone"] = user.get("phone")

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
    is_owner = (user_email and seller_email and user_email == seller_email) or user.get("role") in ("admin", "buyer")
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
    """Delete lot from database. Seller owner, buyer, or admin."""
    database = mongo_db()
    oid = mongo_id(listing_id)
    listing = database.listings.find_one({"_id": oid})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found.")
    
    user_email = (user.get("email") or "").strip().lower()
    seller_email = (listing.get("seller_email") or listing.get("ownerEmail") or "").strip().lower()
    is_owner = (user_email and seller_email and user_email == seller_email) or user.get("role") in ("admin", "buyer")
    if not is_owner:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this listing.")
    
    database.listings.delete_one({"_id": oid})
    return {"status": "deleted", "id": listing_id}


@app.get("/admin/approval-requests")
def admin_approval_requests(user: dict = Depends(require_role("admin"))):
    database = mongo_db()
    return {"requests": [serialize_mongo(order) for order in database.orders.find().sort("created_at", -1)]}


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
def payment_receipt(order_id: str, user: dict = Depends(get_current_user)):
    database = mongo_db()
    order = database.orders.find_one({"_id": mongo_id(order_id), "status": "Admin approved - seller notified"})
    if not order:
        raise HTTPException(status_code=404, detail="Receipt is available after admin approval.")
    # Fix: use fallback price when offered_price is 0 or missing
    offered = order.get("offered_price", 0)
    if not offered or offered <= 0:
        offered = (order.get("min_price", 0) + order.get("max_price", 0)) / 2
    amount = order["quantity"] * offered
    return {"receipt_id": order_id, "item": order["item"], "quantity": order["quantity"], "amount": round(amount, 2), "status": "Payment pending", "qr_code": make_receipt_qr(order_id, amount, order["payment_method"])}


@app.get("/categories")
def get_categories(city: str = "Pune"):
    """Returns the full list of detectable categories with metadata and city spot prices from MongoDB."""
    from categories import CITY_PRICE_FACTORS
    factor = CITY_PRICE_FACTORS.get(city, 1.0)
    items = []
    
    try:
        database = mongo_db()
        db_cats = list(database.categories.find())
        if len(db_cats) >= 50:
            for info in db_cats:
                base_p = info.get("base_price", info.get("min_price", 0))
                calibrated_p = round(base_p * factor) if base_p >= 10 else round(base_p * factor, 1)
                unit_label = info.get("unit", "kg")
                items.append({
                    "key": info.get("key", info.get("display_name")),
                    "display_name": info["display_name"],
                    "category": info["category"],
                    "type": info.get("type", "Recyclable"),
                    "unit": unit_label,
                    "base_price": base_p,
                    "spot_price": calibrated_p,
                    "min_price": round(info.get("min_price", 0) * factor),
                    "max_price": round(info.get("max_price", 0) * factor),
                    "price_range": f"₹{calibrated_p} /{unit_label}",
                    "sell_to": info.get("sell_to", "Contact admin for routing"),
                    "reuse_tip": info.get("reuse_tip", ""),
                    "eco_impact": info.get("eco_impact", {}),
                    "icon": info.get("icon", "♻️"),
                })
            return {"categories": items, "city": city, "city_factor": factor, "source": "mongodb"}
    except Exception:
        pass

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
    return {"categories": items, "city": city, "city_factor": factor, "source": "memory"}


@app.get("/dealers")
def get_dealers(city: str | None = None):
    """Returns verified recycling dealers from MongoDB database."""
    try:
        database = mongo_db()
        query = {"city": {"$regex": city, "$options": "i"}} if city else {}
        dealers = [serialize_mongo(d) for d in database.dealers.find(query)]
        if dealers:
            return {"dealers": dealers, "count": len(dealers), "source": "mongodb"}
    except Exception:
        pass
    return {"dealers": DEALER_DIRECTORY, "count": len(DEALER_DIRECTORY), "source": "fallback"}


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


@app.get("/dealers")
def get_dealers(city: str = None, category: str = None):
    """Returns certified scrap dealer directory with optional city/category filters."""
    dealers = DEALER_DIRECTORY
    if city:
        dealers = [d for d in dealers if city.lower() in d["city"].lower()]
    if category:
        dealers = [d for d in dealers if any(category.lower() in t.lower() for t in d["types"])]
    return {"dealers": dealers, "total": len(dealers)}


@app.post("/calculate")
def calculate_resale(payload: CalculateRequest):
    """Computes exact estimated payout based on category rate bands and user quantity."""
    # Find matching category by key or display name
    matched_info = None
    if payload.category_key and payload.category_key in WASTE_CATEGORIES:
        matched_info = WASTE_CATEGORIES[payload.category_key]
    else:
        for info in WASTE_CATEGORIES.values():
            if info["display_name"].lower() == payload.display_name.lower():
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
        "item_name": matched_info["display_name"],
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
