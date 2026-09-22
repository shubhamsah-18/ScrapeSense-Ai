<<<<<<< HEAD
# ⚙️ ScrapSense AI — Smart Scrap & Waste Valuation Platform

> Zero-shot AI waste classification + dynamic scrap pricing + eco-impact analytics + admin-mediated marketplace

## 🚀 Features

- **CLIP Vision AI**: Zero-shot classification using OpenAI CLIP ViT-B/32 — no training data needed
- **Dynamic Pricing Calculator**: Real-time resale estimation based on scrap category, quantity & market rates
- **Eco-Impact Metrics**: CO₂ offset, energy savings, and circular economy badges per material
- **Admin-Mediated Marketplace**: Seller → Admin verification → Buyer purchase flow
- **JWT Authentication**: Secure token-based auth with role-based access control (Seller/Buyer/Admin)
- **OTP Registration**: Email-based OTP verification for new accounts
- **Dealer Directory**: Certified scrap dealer listings across Indian metros
- **Print-Ready Receipt**: Scrap valuation slip with QR code

## 📂 Project Structure

```
scrap-recycle-ai/
├── backend/
│   ├── main.py              # FastAPI server (API endpoints)
│   ├── auth.py              # JWT authentication & RBAC module
│   ├── categories.py        # Scrap knowledge base (26 items + dealer directory)
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html           # Main SPA (all roles: seller/buyer/admin)
│   ├── script.js            # Frontend application logic
│   └── style.css            # Design system & responsive styles
├── .env                     # Environment variables (not committed)
├── .env.example             # Environment template
├── run.py                   # Unified launcher (frontend + backend)
├── start.bat                # Windows quick start
└── start.ps1                # PowerShell quick start
```

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- MongoDB (for auth & marketplace features)
- ~600MB disk space (for CLIP model download on first run)

### Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd scrap-recycle-ai

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env with your settings

# 5. Start MongoDB (if not already running)
mongod

# 6. Launch application
python run.py
```

The app opens automatically at `http://127.0.0.1:5500`

## 🔌 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | No | Server health check |
| GET | `/categories` | No | Scrap material catalog |
| GET | `/dealers` | No | Certified dealer directory |
| GET | `/stats` | No | Platform statistics |
| GET | `/ai/status` | No | Multi-provider AI status (OpenAI, Claude, Astra, Astra DB) |
| POST | `/ai/chat` | No | AI Recycling Chatbot Copilot with model selection |
| GET | `/ai/chat/history` | No | Retrieve chat conversation from Astra DB |
| POST | `/predict` | No | AI scrap image classification (CLIP / GPT-4o / Claude / Astra) |
| POST | `/calculate` | No | Resale value calculator |
| POST | `/auth/request-otp` | No | Request registration OTP |
| POST | `/auth/verify-otp` | No | Verify OTP & create account |
| POST | `/auth/login` | No | Login (returns JWT token) |
| POST | `/listings` | JWT | Create scrap listing |
| GET | `/listings` | JWT | Get verified listings |
| POST | `/approval-requests` | JWT | Buyer purchase request |
| GET | `/orders` | JWT | User's order history |
| GET | `/admin/users` | Admin | All registered accounts |
| GET | `/admin/listings` | Admin | All listings (incl. unverified) |
| PATCH | `/listings/{id}/verify` | Admin | Approve/reject listing |
| GET | `/admin/approval-requests` | Admin | Pending purchase requests |
| PATCH | `/admin/approval-requests/{id}` | Admin | Approve/reject purchase |
| GET | `/payments/receipt/{id}` | JWT | Transaction receipt + QR |

## 🔐 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | empty | OpenAI API key for GPT-4o chat & vision |
| `OPENAI_MODEL` | `gpt-4o` | Active OpenAI model |
| `ANTHROPIC_API_KEY` | empty | Anthropic API key for Claude 3.5 Sonnet |
| `ANTHROPIC_MODEL` | `claude-3-5-sonnet-20241022` | Active Anthropic model |
| `GEMINI_API_KEY` | empty | Google API key for Project Astra / Gemini 1.5 |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Active Google Gemini model |
| `ASTRA_DB_APPLICATION_TOKEN` | empty | DataStax Astra DB Application Token |
| `ASTRA_DB_API_ENDPOINT` | empty | DataStax Astra DB JSON API Endpoint |
| `ASTRA_DB_KEYSPACE` | `default_keyspace` | Astra DB Keyspace name |
| `DEFAULT_AI_PROVIDER` | `gemini` | Default AI model provider |
| `JWT_SECRET_KEY` | auto-generated | Secret key for JWT signing |
| `ADMIN_LOGIN` | `7488114039` | Admin username |
| `ADMIN_PASSWORD` | `12341234` | Admin password |
| `MONGODB_URI` | `mongodb://127.0.0.1:27017` | MongoDB connection string |
| `MONGODB_DATABASE` | `scrapsense` | Database name |
| `DISABLE_TORCH` | `false` | Run without local CLIP model |
| `CORS_ORIGINS` | `localhost:5500` | Allowed CORS origins |
| `DEV_OTP_MODE` | `true` | Log OTPs to console |
| `SMTP_HOST` | empty | SMTP server for OTP emails |

## 🧠 Algorithms

### 1. CLIP Zero-Shot Classification
Uses OpenAI's CLIP ViT-B/32 model to match image embeddings against natural language scrap descriptions using cosine similarity and softmax scoring.

### 2. Dynamic Resale Pricing
Calculates estimated payout using category-specific min/max rate bands multiplied by user-specified quantity.

### 3. Eco-Impact Calculator
Computes CO₂ offset, energy savings, and water conservation metrics per material type and quantity.

### 4. JWT Authentication
HMAC-SHA256 signed tokens with 24h expiry, bcrypt password hashing, and role-based access control.

### 5. OTP Verification
Time-limited (10min) 6-digit codes with bcrypt hashing, max 5 attempts, and MongoDB TTL auto-cleanup.

### 6. Inventory Management
Automatic quantity deduction on order approval with SOLD status transition when stock reaches zero.

## 🛠️ Tech Stack

- **Backend**: FastAPI + PyTorch + Transformers (CLIP) + PyMongo
- **Frontend**: Vanilla HTML5 + CSS3 + JavaScript (SPA)
- **Database**: MongoDB
- **AI Model**: OpenAI CLIP ViT-B/32 (zero-shot)
- **Auth**: JWT (PyJWT) + bcrypt

## 📝 License

Final Year Engineering Project — Computer Science & Engineering
=======
# ScrapeSense-Ai
A full-stack AI scraping, smart valuation, and marketplace platform featuring a unified launcher for FastAPI and frontend servers.
>>>>>>> a83e45b14cc01a1cba984906a653a5a03404066b
