# ScrapSense AI - Verified Technical Architecture & System Analysis

**Document Status:** Ground-Truth Verified Implemented Behavior  
**Specification Version:** 2.0.0 (Phase 2 Audited)  
**Date:** September 2026  

---

## 1. Executive Summary & Runtime Architecture

This deliverable documents the actual implemented behavior of the **ScrapSense AI** codebase, verified through static code analysis, execution traces, and regression test suites. Claims made in marketing documents or outdated README files are superseded by the findings below.

### 1.1 Dual Runtime Paths

The application supports two distinct execution paths:

```
+------------------------------------------------------------------------------------+
|                                    RUNTIME PATHS                                   |
+--------------------------------------------------+---------------------------------+
| LOCAL RUNTIME (run.py)                           | VERCEL RUNTIME (api/index.py)   |
|--------------------------------------------------+---------------------------------|
| - Concurrent Python Execution                    | - Serverless Function Handler   |
|   1. Uvicorn FastAPI Server on port 8000         | - vercel.json routes all /(.*)  |
|   2. ThreadingHTTPServer on port 5500            |   traffic to api/index.py       |
| - Serves frontend/ directly via Python HTTP      | - Dynamically prepends backend/ |
| - Mounts / fallback to frontend/index.html       |   to sys.path and imports app   |
|   via FileResponse when Accept: text/html        | - Resolves public/index.html    |
| - Full local network broadcast (0.0.0.0)         |   (falling back to frontend/)   |
| - CLI reseeding and database inspection tools    | - Ephemeral serverless state    |
+--------------------------------------------------+---------------------------------+
```

#### Local Path Execution Sequence (`run.py` & `backend/main.py`)
1. `run.py` starts two parallel background threads:
   - **Frontend Thread:** Instantiates `ThreadingHTTPServer(("0.0.0.0", 5500), CORSHTTPRequestHandler)` serving static files out of `frontend/`.
   - **Backend Thread:** Launches `uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)`.
2. Discoverable LAN IP addresses are collected across all network interfaces using `socket.getaddrinfo` to enable mobile browser and QR-code camera pairing.
3. FastAPI's root endpoint (`GET /`) checks incoming `Accept` headers; if `text/html` is requested, it directly serves `frontend/index.html` as a fallback SPA entrypoint.

#### Vercel Serverless Path (`api/index.py` & `vercel.json`)
1. Incoming HTTP requests are matched against `vercel.json` routing configuration:
   - Root `/` and static assets map to `public/` or `api/index.py`.
   - Rewrites route all matching requests `/(.*)` to `api/index.py`.
2. `api/index.py` appends the project root and `backend/` to `sys.path`.
3. It imports `app` from `backend.main` and exposes it as the ASGI entrypoint for Vercel's Python runtime.
4. Static file delivery relies on `public/index.html`, with graceful fallback to `frontend/index.html` if `public/` is omitted in build artifacts.

---

## 2. Startup Sequence & Dependency Initialization

The application lifecycle is managed via FastAPI's `lifespan` asynchronous context manager in `backend/main.py`:

```
+--------------------------------------------------------------------+
|                   STARTUP SEQUENCE (backend/main.py)               |
+--------------------------------------------------------------------+
                                   │
                                   ▼
          [1] Load Environment Variables & Configuration
              - Reads MONGODB_URI, DB_NAME, JWT_SECRET, PORT
                                   │
                                   ▼
          [2] MongoDB Connectivity & Client Establishment
              - Instantiates MongoClient with serverSelectionTimeoutMS=5000
              - Checks ping / connection readiness
                                   │
                                   ▼
          [3] Phase 2 Seed-If-Empty Initialization
              - Calls seed_database(seed_if_empty=True)
              - Checks if collections exist & contain documents
              - If empty: populates categories, dealers, users, lots, orders
              - If populated: preserves all user records and listings
                                   │
                                   ▼
          [4] Zero-Shot AI Vision Model Loading (load_model())
              - Checks DISABLE_TORCH environment flag
              - If disabled or missing: activates heuristic simulation mode
              - If enabled: loads CLIPModel ('openai/clip-vit-base-patch32')
                and CLIPProcessor to CPU or CUDA
                                   │
                                   ▼
          [5] CORS Middleware & Route Table Registration
              - Applies CORSMiddleware with configured origins
              - Binds API routers, auth controllers, and static handlers
```

---

## 3. External Services & Environment Variables

| Variable | Required | Default Value | Description |
|:---|:---:|:---|:---|
| `MONGODB_URI` | No | `mongodb://127.0.0.1:27017` | MongoDB connection URI (local instance or Atlas cluster) |
| `DB_NAME` | No | `scrapsense` | Target database name |
| `ADMIN_LOGIN` | No | `admin` | Default administrative login credential ID |
| `ADMIN_PASSWORD` | No | `admin123` | Default administrative password (hashed with salt upon seed) |
| `JWT_SECRET` | No | `scrapsense_jwt_secret_dev_key_2026_x` | Secret key used for signing HMAC-SHA256 JWT session tokens |
| `JWT_ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `CORS_ORIGINS` | No | `*` | Allowed CORS origins (comma-separated or wildcard) |
| `DISABLE_TORCH` | No | `false` | When `true`, bypasses PyTorch/Transformers heavy model loading |
| `DEV_OTP_MODE` | No | `true` | When `true`, returns generated OTP in API response preview for dev testing |
| `OPENAI_API_KEY` | No | `""` | Optional key for live OpenAI GPT vision/assistant fallback |
| `ANTHROPIC_API_KEY` | No | `""` | Optional key for live Claude assistant queries |
| `GEMINI_API_KEY` | No | `""` | Optional key for Google Gemini / Astra LLM queries |
| `PORT` | No | `8000` | Backend listening port |
| `HOST` | No | `0.0.0.0` | Backend bind host |

### External Service Dependencies
1. **MongoDB Server**: Acts as the primary persistent database. If unavailable or down, the backend falls back to in-memory static categories and dealer directories without crashing.
2. **Hugging Face Hub / Transformers**: Downloads and caches `openai/clip-vit-base-patch32` weights (~600MB) on first start unless `DISABLE_TORCH=true`.
3. **Nominatim OpenStreetMap**: Client-side reverse geocoding API queried to resolve latitude and longitude into human-readable Indian city and state names.
4. **LLM Vision Providers (OpenAI, Anthropic, Google Gemini)**: Secondary advisory channels invoked via `/ai/chat` if configured.

---

## 4. CORS Origins & Security Constraints

The backend implements `CORSMiddleware` in `backend/main.py`:

```python
cors_origins_raw = os.getenv("CORS_ORIGINS", "*")
cors_origins = [o.strip() for o in cors_origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Observed Behavior & Security Implications
- When `CORS_ORIGINS` is unset, it defaults to `["*"]`.
- According to the W3C Fetch Specification, web browsers block responses with `Access-Control-Allow-Origin: *` when `Access-Control-Allow-Credentials: true` is set.
- In modern desktop and mobile browsers, local cross-origin requests from `http://127.0.0.1:5500` to `http://127.0.0.1:8000` work when the origin is explicitly included or when served from the unified port 8000. In strict cloud production deployments, `CORS_ORIGINS` must be explicitly defined (e.g., `https://scrapsense.vercel.app`).

---

## 5. Scrap Pricing Engine & Mandi Heuristics

All scrap rates, commodity ranges, and payout valuations in ScrapSense AI are derived from heuristic algorithms rather than live commodity terminal feeds:

```
[User Input: Item / Category + Quantity (kg/unit) + Selected City]
                              │
                              ▼
        [Base Price & Band Lookup (WASTE_CATEGORIES)]
        - Base Price (min_price, max_price)
                              │
                              ▼
        [City Factor Multiplier (CITY_FACTORS)]
        - Mumbai: 1.04 (+4%)       - Pune:      1.02 (+2%)
        - Delhi:  1.03 (+3%)       - Jaipur:    0.98 (-2%)
        - Default City: 1.00
                              │
                              ▼
        [Calculation & Projections (/calculate)]
        - Spot Price     = Round(Base Price * City Factor)
        - Expected Total = Round(Quantity * Spot Price)
        - Value Range    = [Qty * Min Rate, Qty * Max Rate]
        - Eco-Impact     = kg CO2 Diverted + Metal Recovery %
```

> **Ground-Truth Note:** Prices reflect curated Indian regional benchmarks (Jaipur, Pune, Mumbai, Delhi scrap yards). They are estimates for recycling estimation and negotiation, not real-time live stock/commodity exchange market quotes.

---

## 6. Duplicate UI Directories (`frontend/` vs `public/`)

The repository contains two parallel directories housing frontend code:

| Directory | Primary Consumer | Purpose & Contents |
|:---|:---|:---|
| `frontend/` | Local Dev Runner (`run.py`) & FastAPI `FileResponse` | Contains `index.html`, `style.css`, `script.js`, `sw.js`, audio files, and test mocks. Port 5500 serves directly from here. |
| `public/` | Vercel Deployment (`api/index.py` & `vercel.json`) | Contains duplicate copies of `index.html`, `style.css`, `script.js`, `manifest.json`. Vercel serverless builds deploy static assets from `public/`. |

### Synchronization Mandate
To prevent silent regression and behavior drift across local and Vercel environments, any modification to `frontend/script.js` or `frontend/index.html` must be kept byte-for-byte identical with `public/script.js` and `public/index.html`.

---

## 7. Complete API Route Table

| HTTP Method | Route Endpoint | Authentication / Role | Input Payload | Output / Status | Failure Codes |
|:---|:---|:---|:---|:---|:---|
| `GET` | `/` | Public | None | Service metadata JSON or `index.html` | 200 |
| `GET` | `/health` | Public | None | `{"status": "healthy", "device": "..."}` | 200 |
| `GET` | `/network-info` | Public | None | Primary IP, frontend/backend ports, mobile URL | 200 |
| `GET` | `/categories` | Public | Query: `city` (optional) | List of 130 categories with city factor | 200 |
| `GET` | `/dealers` | Public | Query: `city`, `category` | Filtered recyclers directory (`total == count`) | 200 |
| `GET` | `/stats` | Public | None | Category counts, groups, active dealers | 200 |
| `POST` | `/calculate` | Public | JSON: `category_key`, `display_name`, `quantity` | Projected payout range and eco impact | 200, 422 |
| `POST` | `/predict` | Public | Multipart: `file` (image) | CLIP classification prediction & confidence | 200, 400, 422 |
| `POST` | `/auth/login` | Public | JSON: `email`, `password`, `role` | JWT token, user profile, httpOnly cookie | 200, 401, 429 |
| `POST` | `/auth/register` | Public | JSON: `name`, `email`, `password`, `role` | JWT token, user profile, httpOnly cookie | 200, 400, 409, 422 |
| `POST` | `/auth/request-otp`| Public | JSON: `email`, `role`, `name`, `password` | OTP dispatch notice + dev preview | 200, 400, 429 |
| `POST` | `/auth/verify-otp` | Public | JSON: `email`, `otp`, `role` | Account creation, JWT token, session cookie | 200, 401, 410, 429 |
| `POST` | `/auth/logout` | Public | None | Clears httpOnly `scrapsense_session` cookie | 200 |
| `GET` | `/auth/me` | Authenticated | None | Current user record from token | 200, 401 |
| `GET` | `/listings` | Public | None | List of verified marketplace lots | 200 |
| `POST` | `/listings` | **Seller, Admin** | JSON: `item`, `category`, `quantity`, `unit`, `min_price`, `max_price`, etc. | `{"id": "...", "status": "published"}` | 200, 401, 403, 422 |
| `PATCH`| `/listings/{id}` | **Owning Seller, Admin** | JSON: Listing update fields | Updated listing object | 200, 401, 403, 404 |
| `DELETE`| `/listings/{id}`| **Owning Seller, Admin** | None | Deletion confirmation | 200, 401, 403, 404 |
| `GET` | `/seller/listings` | **Seller** | None | Seller's own listings (verified & pending) | 200, 401, 403 |
| `PATCH`| `/listings/{id}/verify`| **Admin** | Query: `approved` (bool) | Verification status update | 200, 401, 403, 404 |
| `POST` | `/approval-requests`| **Buyer, Admin** | JSON: `listing_id`, `offered_price`, `buyer_decision`, `address`, `payment_method` | `{"id": "...", "status": "..."}` | 200, 401, 403, 404, 422 |
| `GET` | `/orders/{id}/receipt`| **Order Buyer, Seller, Admin** | None | HTML receipt slip with cryptographic hash | 200, 401, 403, 404 |
| `GET` | `/payments/receipt/{id}`| **Order Buyer, Seller, Admin** | None | HTML receipt slip (alias) | 200, 401, 403, 404 |
| `GET` | `/seller/sell-requests`| **Seller** | None | All sell requests & deals for seller | 200, 401, 403 |
| `GET` | `/buyer/sell-requests`| **Buyer** | None | All orders & bids for buyer | 200, 401, 403 |
| `PATCH`| `/buyer/sell-requests/{id}/approve` | **Buyer** | None | Buyer approval status transition | 200, 401, 403, 404 |
| `PATCH`| `/buyer/sell-requests/{id}/reject` | **Buyer** | None | Buyer rejection status transition | 200, 401, 403, 404 |
| `GET` | `/admin/deals` | **Admin** | None | All transaction records across system | 200, 401, 403 |
| `PATCH`| `/admin/deals/{id}/clear` | **Admin** | JSON: `action`, `clearance_notes` | Signed clearance certificate & contract ID | 200, 401, 403, 404 |
| `GET` | `/admin/deals/{id}/contract` | **Order Buyer, Seller, Admin** | None | Printable official contract slip | 200, 401, 403, 404 |
| `GET` | `/admin/users` | **Admin** | None | User directory with roles | 200, 401, 403 |
| `GET` | `/admin/analytics` | **Admin** | None | Aggregated circular economy metrics | 200, 401, 403 |
| `GET` | `/ai/status` | Public | None | Status of AI providers | 200 |
| `POST` | `/ai/chat` | Public | JSON: `message`, `provider`, `history` | AI recycling guidance response | 200 |

---

## 8. Authentication & Authorization Model

```
+-------------------------------------------------------------------------+
|                       AUTHENTICATION & RBAC FLOW                        |
+-------------------------------------------------------------------------+

  Incoming Request
         │
         ├── Header: Authorization: Bearer <JWT>
         └── Cookie: scrapsense_session=<JWT>
         │
         ▼
  [get_current_user Dependency]
         │
         ├── 1. Extract token from header or cookie
         ├── 2. Decode HMAC-SHA256 signature using JWT_SECRET
         ├── 3. Verify expiration (exp claim)
         ├── 4. Look up user by email in database.users (or admin profile)
         │      └── If invalid/expired: Raise 401 Unauthorized
         │
         ▼
  [require_role(*allowed_roles)]
         │
         ├── Inspect user["role"]
         │      ├── Role matches allowed roles -> Allow execution
         │      └── Role mismatch -> Raise 403 Forbidden ("Access forbidden for role")
         │
         ▼
  [Resource-Level Ownership Enforcement (Phase 2)]
         ├── POST /listings: seller_email bound to authenticated user token
         ├── PATCH / DELETE /listings/{id}: Must be owner or admin
         ├── POST /approval-requests: buyer_email bound to authenticated user token
         └── Receipts: Caller must be order buyer, seller, or admin
```

---

## 9. MongoDB Database Architecture

The system utilizes MongoDB database `scrapsense` structured across 7 operational collections:

### 1. `categories`
- **Purpose**: Master catalog of 130 authentic Indian recyclable commodities.
- **Key Fields**: `key` (str), `display_name` (str), `category` (str), `type` (str), `unit` (str), `base_price` (float), `min_price` (float), `max_price` (float), `spot_price` (float), `price_range` (str), `sell_to` (str), `reuse_tip` (str), `eco_impact` (dict: `co2_kg`, `energy_kwh`, `water_l`), `icon` (str), `created_at` (datetime).
- **Indexes**: `key` (unique), `category` (asc).

### 2. `dealers`
- **Purpose**: Verified directory of certified Indian scrap yards, smelters, and dismantlers.
- **Key Fields**: `name` (str), `types` (list[str]), `city` (str), `state` (str), `phone` (str), `email` (str), `badge` (str), `address` (str), `accepts` (list[str]), `rating` (float), `verified` (bool).
- **Indexes**: `city` (asc), `types` (asc).

### 3. `users`
- **Purpose**: Authenticated user identity store supporting RBAC (`admin`, `seller`, `buyer`).
- **Key Fields**: `name` (str), `email` (str, lowercase), `role` (str), `password_hash` (str), `salt` (str), `phone` (str), `city` (str), `state` (str), `otp_verified` (bool), `created_at` (datetime), `last_login` (datetime), `login_count` (int).
- **Indexes**: `email` (unique).

### 4. `listings`
- **Purpose**: Public & admin-moderated scrap lots submitted by verified sellers.
- **Key Fields**: `item` (str), `category` (str), `quantity` (float), `unit` (str), `city` (str), `state` (str), `note` (str), `min_price` (float), `max_price` (float), `photo` (str base64), `seller` (str), `seller_email` (str), `seller_phone` (str), `ownerEmail` (str), `verified` (bool), `verified_at` (datetime), `created_at` (datetime).
- **Indexes**: `verified` (asc), `seller_email` (asc), `created_at` (desc).

### 5. `orders`
- **Purpose**: Formal deal lifecycles, purchase agreements, buyer approvals, and cleared contracts.
- **Key Fields**: `lot` (str), `item` (str), `category` (str), `buyer` (str), `buyer_name` (str), `buyer_email` (str), `seller` (str), `seller_email` (str), `seller_phone` (str), `seller_location` (str), `quantity` (float), `unit` (str), `offered_price` (float), `min_price` (float), `max_price` (float), `payment` (str), `payment_method` (str), `address` (str), `status` (str), `buyer_decision` (str), `admin_cleared` (bool), `admin_cleared_by` (str), `admin_notes` (str), `contract_id` (str), `contract_number` (str), `created_at` (datetime), `decided_at` (datetime), `admin_cleared_at` (datetime).
- **Indexes**: `buyer_email` (asc), `seller_email` (asc), `status` (asc), `created_at` (desc).

### 6. `otp_requests`
- **Purpose**: Ephemeral signup verification challenges with automated 10-minute expiry.
- **Key Fields**: `email` (str), `role` (str), `name` (str), `password_hash` (str), `salt` (str), `otp_hash` (str), `otp_salt` (str), `expires_at` (float timestamp), `attempts` (int), `created_at` (datetime).
- **Indexes**: `email` (asc), `expires_at` (TTL).

### 7. `analytics`
- **Purpose**: Platform-wide circular economy statistics and environmental aggregation.
- **Key Fields**: `platform_name` (str), `version` (str), `total_categories_tracked` (int), `total_active_dealers` (int), `total_registered_users` (int), `total_scrap_inventory_weight_kg` (float), `total_scrap_inventory_units` (float), `estimated_co2_offset_tonnes` (float), `precious_metals_recovery_rate` (str), `active_mandi_cities` (list[str]), `ai_model` (str), `updated_at` (datetime).

---

## 10. Test Coverage & Verified Regression Status

Unit and regression testing is managed via `pytest` executing against FastAPI's `TestClient` in `backend/tests/test_api.py`.

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0
collected 24 items

backend/tests/test_api.py::TestHealthEndpoints::test_root_returns_ok            PASSED [  4%]
backend/tests/test_api.py::TestHealthEndpoints::test_health_check              PASSED [  8%]
backend/tests/test_api.py::TestHealthEndpoints::test_network_info              PASSED [ 12%]
backend/tests/test_api.py::TestCategoryEndpoints::test_get_categories          PASSED [ 16%]
backend/tests/test_api.py::TestCategoryEndpoints::test_get_categories_with_city PASSED [ 20%]
backend/tests/test_api.py::TestCategoryEndpoints::test_get_stats               PASSED [ 25%]
backend/tests/test_api.py::TestCategoryEndpoints::test_get_dealers             PASSED [ 29%]
backend/tests/test_api.py::TestCategoryEndpoints::test_get_dealers_with_category_filter PASSED [ 33%]
backend/tests/test_api.py::TestCalculateEndpoint::test_calculate_resale_basic  PASSED [ 37%]
backend/tests/test_api.py::TestCalculateEndpoint::test_calculate_resale_by_display_name PASSED [ 41%]
backend/tests/test_api.py::TestAIEndpoints::test_ai_status                     PASSED [ 45%]
backend/tests/test_api.py::TestAIEndpoints::test_ai_chat_returns_response      PASSED [ 50%]
backend/tests/test_api.py::TestAuthEndpoints::test_admin_login_success         PASSED [ 54%]
backend/tests/test_api.py::TestAuthEndpoints::test_admin_login_invalid         PASSED [ 58%]
backend/tests/test_api.py::TestAuthEndpoints::test_protected_endpoint_no_auth  PASSED [ 62%]
backend/tests/test_api.py::TestPredictEndpoint::test_predict_rejects_non_image  PASSED [ 66%]
backend/tests/test_api.py::TestPhase2SecurityAndRBAC::test_post_listings_no_token PASSED [ 70%]
backend/tests/test_api.py::TestPhase2SecurityAndRBAC::test_patch_listings_no_token PASSED [ 75%]
backend/tests/test_api.py::TestPhase2SecurityAndRBAC::test_delete_listings_no_token PASSED [ 79%]
backend/tests/test_api.py::TestPhase2SecurityAndRBAC::test_post_approval_requests_no_token PASSED [ 83%]
backend/tests/test_api.py::TestPhase2SecurityAndRBAC::test_get_receipt_no_token PASSED [ 87%]
backend/tests/test_api.py::TestPhase2SecurityAndRBAC::test_post_listings_wrong_role PASSED [ 91%]
backend/tests/test_api.py::TestPhase2SecurityAndRBAC::test_post_approval_requests_wrong_role PASSED [ 95%]
backend/tests/test_api.py::TestSeedIfEmptyMode::test_seed_if_empty_skips_when_collections_contain_data PASSED [100%]
============================== 24 passed in 10.03s ==============================
```

### Untested Workflows & Integration Gaps
1. **Live SMTP Dispatch**: Email OTP transmission is simulated in dev mode (`DEV_OTP_MODE=true`); end-to-end integration with third-party transactional mailers (SendGrid/AWS SES) is untested.
2. **PyTorch GPU Inference**: Test runner defaults to `DISABLE_TORCH=true` to guarantee sub-second headless execution; CUDA device transfers require dedicated GPU integration testing.
3. **PWA Offline Service Worker Sync**: Background sync when offline during a network drop requires browser subagent automation.
4. **Payment Gateway Webhooks**: Live Razorpay/Cashfree payment confirmation hooks are mocked via instantaneous transaction records.

---

## 11. Ranked Security & Architectural Findings

| Rank | Severity | Issue Summary | Ticket / Action Plan |
|:---:|:---:|:---|:---|
| **1** | **CRITICAL** | **Unauthenticated / Unchecked Listing Deletion & Modification**<br>Any user could mutate or delete any listing by ID without session or ownership verification. | **FIXED in Phase 2** (`backend/main.py`) |
| **2** | **CRITICAL** | **Listing Creation Impersonation & Lack of Role Restriction**<br>`POST /listings` allowed unauthenticated callers to post lots spoofing any seller email. | **FIXED in Phase 2** (`backend/main.py`) |
| **3** | **HIGH** | **Unrestricted Purchase & RFQ Dispatch**<br>`POST /approval-requests` allowed unauthenticated users to create binding purchase orders. | **FIXED in Phase 2** (`backend/main.py`) |
| **4** | **HIGH** | **Order Receipt Information Disclosure**<br>Receipt slips containing private addresses and financial amounts were viewable by arbitrary callers. | **FIXED in Phase 2** (`backend/main.py`) |
| **5** | **HIGH** | **Destructive Database Startup Purge**<br>Server startup unconditionally purged registered users, marketplace listings, and active orders. | **FIXED in Phase 2** (`backend/seed_db.py` & `backend/main.py`) |
| **6** | **HIGH** | **Duplicate Conflicting Dealer Route Handlers**<br>Two `GET /dealers` handlers existed; the second masked MongoDB queries and returned mismatched `total` vs `count`. | **FIXED in Phase 2** (`backend/main.py`) |
| **7** | **MEDIUM** | **Wildcard CORS with Credentials in Cloud Deployment**<br>`allow_origins=["*"]` with `allow_credentials=True` is rejected by browsers in cross-origin environments. | **Deferred to Follow-Up** (CORS Agent) |
| **8** | **MEDIUM** | **Service Worker Offline Cache Invalidation**<br>`sw.js` caches static scripts; cache name bump required upon release to prevent stale client assets. | **Deferred to Follow-Up** (Service Worker Agent) |
| **9** | **MEDIUM** | **Stateful Session Revocation / Token Blocklist**<br>JWTs cannot be revoked server-side prior to expiration if a user logs out early. | **Deferred to Follow-Up** (Session Agent) |
| **10**| **LOW** | **Duplicate Asset Drift Risk (`frontend/` vs `public/`)**<br>Redundant folders increase risk of divergent edits between local and Vercel environments. | **Deferred to Follow-Up** (Asset Agent) |
| **11**| **LOW** | **Database Test Isolation with Live MongoDB Mocking**<br>Test suite uses mock stubs; needs Testcontainers or ephemeral MongoDB fixture. | **Deferred to Follow-Up** (Test Agent) |
