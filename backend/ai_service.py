"""
ScrapSense AI - Multi-Provider AI Service
-----------------------------------------
Unified engine supporting:
  - OpenAI (GPT-4o, GPT-4o-mini)
  - Anthropic (Claude 3.5 Sonnet, Claude 3 Haiku)
  - Google Astra / Gemini (Gemini 1.5 Flash, Gemini 1.5 Pro)
  - DataStax Astra DB (Vector / Document Store for chat history and recycling knowledge)

Includes domain-expert prompting for Indian scrap and electronic waste valuation,
multimodal vision inspection, and smart simulation fallback when keys are absent.
"""

import os
import io
import json
import base64
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import requests

from categories import WASTE_CATEGORIES, CITY_PRICE_FACTORS

# ---------------- CONFIGURATION ----------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o").strip()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022").strip()

GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN", "").strip()
ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT", "").strip().rstrip("/")
ASTRA_DB_KEYSPACE = os.getenv("ASTRA_DB_KEYSPACE", "default_keyspace").strip()

DEFAULT_AI_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "gemini").strip().lower()

# Build condensed scrap knowledge snippet for system prompt
def get_scrap_knowledge_summary() -> str:
    lines = []
    for k, v in list(WASTE_CATEGORIES.items())[:30]:
        lines.append(f"- {v['display_name']} ({v.get('category','')}): ₹{v.get('min_price',0)}-{v.get('max_price',0)} /{v.get('unit','kg')}. Tip: {v.get('reuse_tip','')}")
    return "\n".join(lines)

SYSTEM_PROMPT = f"""You are the ScrapSense AI Copilot — an expert AI consultant in Indian scrap metal, electronic waste (e-waste), automotive recycling, and circular economy intelligence.
Your purpose:
1. Provide accurate scrap market valuation in Indian Rupees (₹/kg or ₹/piece) based on current mandi rates.
2. Advise on safe handling, hazardous materials (lead, acid, mercury, beryllium, lithium-ion risks), and environmental protocols.
3. Recommend best recycling pathways: authorized recyclers, component recovery (gold, copper, silver), battery exchanges, and circular reuse.
4. Calculate potential eco-impact (CO2 offset, landfill avoidance, energy conserved).

Current Scrap Knowledge Reference:
{get_scrap_knowledge_summary()}

Tone & Style:
- Helpful, professional, concise, and technically accurate.
- Always use Indian Rupees (₹) for pricing.
- If an item is hazardous, clearly give safety precautions.
- Provide practical recommendations for buyers, sellers, or recyclers.
"""

def get_ai_status() -> Dict[str, Any]:
    """Returns availability of all AI providers and Astra DB connection."""
    providers = {
        "openai": {
            "name": "OpenAI GPT",
            "model": OPENAI_MODEL,
            "configured": bool(OPENAI_API_KEY),
            "version": "GPT-4o / GPT-4o-mini"
        },
        "claude": {
            "name": "Anthropic Claude",
            "model": ANTHROPIC_MODEL,
            "configured": bool(ANTHROPIC_API_KEY),
            "version": "Claude 3.5 Sonnet"
        },
        "gemini": {
            "name": "Google Astra / Gemini",
            "model": GEMINI_MODEL,
            "configured": bool(GEMINI_API_KEY),
            "version": "Project Astra / Gemini 1.5"
        },
        "astradb": {
            "name": "DataStax Astra DB",
            "endpoint": ASTRA_DB_API_ENDPOINT or "Not configured",
            "configured": bool(ASTRA_DB_APPLICATION_TOKEN and ASTRA_DB_API_ENDPOINT),
            "type": "Cloud Vector / Document DB"
        }
    }
    active_default = DEFAULT_AI_PROVIDER
    if active_default not in providers:
        active_default = "gemini"
    return {
        "providers": providers,
        "default_provider": active_default,
        "any_configured": any(p["configured"] for p in providers.values())
    }

# ---------------- DATASTAX ASTRA DB INTEGRATION ----------------
def save_chat_to_astra(session_id: str, role: str, message: str, provider: str, metadata: Optional[Dict] = None) -> bool:
    """Saves chat turns to DataStax Astra DB collection 'scrap_chat_history' via Data API."""
    if not ASTRA_DB_APPLICATION_TOKEN or not ASTRA_DB_API_ENDPOINT:
        return False

    url = f"{ASTRA_DB_API_ENDPOINT}/api/json/v1/{ASTRA_DB_KEYSPACE}/scrap_chat_history"
    headers = {
        "Token": ASTRA_DB_APPLICATION_TOKEN,
        "Content-Type": "application/json"
    }

    doc = {
        "session_id": session_id,
        "role": role,
        "message": message,
        "provider": provider,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {}
    }

    payload = {
        "insertOne": {
            "document": doc
        }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=4)
        if resp.status_code in (200, 201):
            return True
        # If collection doesn't exist, attempt to create it once
        if resp.status_code == 400 and "not exist" in resp.text.lower():
            create_col_url = f"{ASTRA_DB_API_ENDPOINT}/api/json/v1/{ASTRA_DB_KEYSPACE}"
            requests.post(create_col_url, headers=headers, json={"createCollection": {"name": "scrap_chat_history"}}, timeout=4)
            # Retry insert
            resp2 = requests.post(url, headers=headers, json=payload, timeout=4)
            return resp2.status_code in (200, 201)
    except Exception as e:
        print(f"[Astra DB] Sync warning: {e}", flush=True)
    return False

def get_chat_history_from_astra(session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieves chat history from Astra DB."""
    if not ASTRA_DB_APPLICATION_TOKEN or not ASTRA_DB_API_ENDPOINT:
        return []

    url = f"{ASTRA_DB_API_ENDPOINT}/api/json/v1/{ASTRA_DB_KEYSPACE}/scrap_chat_history"
    headers = {
        "Token": ASTRA_DB_APPLICATION_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "find": {
            "filter": {"session_id": session_id},
            "sort": {"timestamp": 1},
            "options": {"limit": limit}
        }
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("data", {}).get("documents", [])
    except Exception as e:
        print(f"[Astra DB] Fetch warning: {e}", flush=True)
    return []

# ---------------- MULTI-MODEL CHAT ENGINE ----------------

def call_openai_chat(message: str, history: List[Dict[str, str]], image_base64: Optional[str] = None) -> str:
    """Calls OpenAI API (GPT-4o)."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not configured in .env")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history[-8:]:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})

    user_content = []
    if image_base64:
        user_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}})
    user_content.append({"type": "text", "text": message})

    messages.append({"role": "user", "content": user_content if image_base64 else message})

    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": OPENAI_MODEL,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 800
        },
        timeout=30
    )
    if resp.status_code != 200:
        raise RuntimeError(f"OpenAI API error ({resp.status_code}): {resp.text}")
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()

def call_claude_chat(message: str, history: List[Dict[str, str]], image_base64: Optional[str] = None) -> str:
    """Calls Anthropic Claude API (Claude 3.5 Sonnet)."""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not configured in .env")

    messages = []
    for h in history[-8:]:
        role = "assistant" if h.get("role") in ("assistant", "model", "bot") else "user"
        messages.append({"role": role, "content": h.get("content", "")})

    user_content = []
    if image_base64:
        user_content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": image_base64
            }
        })
    user_content.append({"type": "text", "text": message})
    messages.append({"role": "user", "content": user_content if image_base64 else message})

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        },
        json={
            "model": ANTHROPIC_MODEL,
            "system": SYSTEM_PROMPT,
            "messages": messages,
            "max_tokens": 800,
            "temperature": 0.3
        },
        timeout=30
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Anthropic Claude API error ({resp.status_code}): {resp.text}")
    data = resp.json()
    text_parts = [p.get("text", "") for p in data.get("content", []) if p.get("type") == "text"]
    return "\n".join(text_parts).strip()

def call_gemini_chat(message: str, history: List[Dict[str, str]], image_base64: Optional[str] = None) -> str:
    """Calls Google Gemini / Project Astra API (Gemini 1.5 Flash)."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured in .env")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

    contents = []
    for h in history[-8:]:
        role = "model" if h.get("role") in ("assistant", "model", "bot") else "user"
        contents.append({"role": role, "parts": [{"text": h.get("content", "")}]})

    user_parts = []
    if image_base64:
        user_parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": image_base64
            }
        })
    user_parts.append({"text": f"{SYSTEM_PROMPT}\n\nUser Question: {message}"})
    contents.append({"role": "user", "parts": user_parts})

    resp = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json={
            "contents": contents,
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 800
            }
        },
        timeout=30
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Google Gemini/Astra API error ({resp.status_code}): {resp.text}")
    data = resp.json()
    candidates = data.get("candidates", [])
    if candidates and "content" in candidates[0]:
        parts = candidates[0]["content"].get("parts", [])
        return "".join([p.get("text", "") for p in parts]).strip()
    return "No response generated by Gemini."

def generate_smart_simulated_reply(message: str, provider: str) -> str:
    """Provides high-quality realistic answers even before user inputs API keys."""
    q = message.lower()
    provider_name = {
        "openai": "OpenAI GPT-4o",
        "claude": "Anthropic Claude 3.5 Sonnet",
        "gemini": "Google Astra (Gemini 1.5)",
        "astra": "Google Astra (Gemini 1.5)"
    }.get(provider, "ScrapSense AI")

    # Domain smart matching
    if "copper" in q:
        return (
            f"**[{provider_name} Valuation & Recycling Intel]**\n\n"
            "🔶 **Copper Scrap Analysis**:\n"
            "- **Current Mandi Spot Rate**: ₹620 – ₹720 / kg (Milberry/bright bare wire commands up to ₹740/kg).\n"
            "- **Grade Separation**: Ensure PVC insulation is stripped; burnt copper wire has lower payout (₹550–₹590/kg) due to oxidation.\n"
            "- **Eco-Impact**: Recycling copper uses **85% less energy** than primary smelting and prevents ~4.5 kg of CO₂ per kg.\n"
            "- **Recycling Channel**: Authorized smelters and certified metal yards listed in our Dealer Directory."
        )
    elif "motherboard" in q or "pcb" in q or "circuit" in q:
        return (
            f"**[{provider_name} E-Waste Intel]**\n\n"
            "🔌 **Motherboard PCB Recovery**:\n"
            "- **Market Rate**: ₹220 – ₹450 / kg (High-grade server boards fetch highest rates due to gold/palladium contacts).\n"
            "- **Safety Precaution**: ⚠️ Never attempt acid extraction or backyard burning; it releases toxic lead and dioxin fumes.\n"
            "- **Valuable Elements**: Gold (edge connectors & CPU sockets), Silver (solder traces), Copper (inner circuit layers).\n"
            "- **Next Step**: Post as a lot on ScrapSense to get verified quotes from authorized CPCB refiners."
        )
    elif "battery" in q or "lithium" in q:
        return (
            f"**[{provider_name} Hazardous Material Warning]**\n\n"
            "🔋 **Battery Disposal & Scrap Value**:\n"
            "- **Lead-Acid Batteries**: ₹85 – ₹115 / kg. Most retail outlets offer direct ₹500–₹1,500 exchange discount on new battery purchases.\n"
            "- **Lithium-Ion / EV Packs**: ₹15,000 – ₹60,000 per pack depending on state-of-health (SoH). Decommissioned packs are valuable for stationary solar storage!\n"
            "- **Safety Note**: Tape terminals to prevent short circuits. Store away from heat and water."
        )
    elif "aluminium" in q or "aluminum" in q:
        return (
            f"**[{provider_name} Metal Valuation]**\n\n"
            "🥫 **Aluminium Scrap Analysis**:\n"
            "- **Spot Price**: ₹125 – ₹185 / kg (Extrusions and clean cookware scrap command premium).\n"
            "- **Eco Efficiency**: Recycling aluminium saves **95% energy** compared to extracting alumina from bauxite ore.\n"
            "- **CO₂ Offset**: ~9.0 kg CO₂ saved per kg recycled."
        )
    else:
        return (
            f"**[{provider_name} Scrap & Recycling Advisor]**\n\n"
            f"Regarding your query: *\"{message}\"*\n\n"
            "ScrapSense AI tracks 26+ electronic components and recyclable scrap categories across major Indian metros.\n"
            "- **Spot Mandi Rates**: We calibrate prices daily with city factors (Mumbai +4%, NCR +2%, Pune 1.00).\n"
            "- **How to Maximize Value**: Clean, segregate, and remove non-metallic impurities before weighing.\n"
            "- **Circular Economy**: Check our Calculator tab for exact payout bands and certified dealer contact options.\n\n"
            "*(💡 Note: To enable live cloud inference directly from OpenAI, Anthropic, or Google Astra, add your API key in `.env`)*"
        )

# ---------------- MAIN DISPATCH FUNCTIONS ----------------

def chat_recycling_assistant(
    message: str,
    history: List[Dict[str, str]],
    provider: str = "gemini",
    image_bytes: Optional[bytes] = None,
    session_id: str = "default_session"
) -> Dict[str, Any]:
    """
    Routes chat query to requested AI provider (openai, claude, gemini/astra)
    with automatic Astra DB synchronization and simulated fallback.
    """
    provider = provider.lower()
    if provider in ("astra", "google"):
        provider = "gemini"

    image_base64 = None
    if image_bytes:
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    used_provider = provider
    live_response = None
    error_note = None

    try:
        if provider == "openai":
            if OPENAI_API_KEY:
                live_response = call_openai_chat(message, history, image_base64)
            else:
                live_response = generate_smart_simulated_reply(message, "openai")
                error_note = "Using simulated GPT-4o response (add OPENAI_API_KEY in .env for live API calls)"

        elif provider == "claude":
            if ANTHROPIC_API_KEY:
                live_response = call_claude_chat(message, history, image_base64)
            else:
                live_response = generate_smart_simulated_reply(message, "claude")
                error_note = "Using simulated Claude response (add ANTHROPIC_API_KEY in .env for live API calls)"

        elif provider == "gemini":
            if GEMINI_API_KEY:
                live_response = call_gemini_chat(message, history, image_base64)
            else:
                live_response = generate_smart_simulated_reply(message, "gemini")
                error_note = "Using simulated Astra/Gemini response (add GEMINI_API_KEY in .env for live API calls)"

        else:
            live_response = generate_smart_simulated_reply(message, "gemini")

    except Exception as exc:
        print(f"[AI Service] Error calling {provider}: {exc}", flush=True)
        live_response = generate_smart_simulated_reply(message, provider)
        error_note = f"API call failed ({str(exc)[:60]}). Showing expert domain answer."

    # Save to Astra DB in background / best-effort
    saved_to_astra = False
    try:
        saved_to_astra = save_chat_to_astra(
            session_id=session_id,
            role="user",
            message=message,
            provider=provider
        )
        save_chat_to_astra(
            session_id=session_id,
            role="assistant",
            message=live_response,
            provider=provider
        )
    except Exception:
        pass

    return {
        "response": live_response,
        "provider": used_provider,
        "model": {
            "openai": OPENAI_MODEL,
            "claude": ANTHROPIC_MODEL,
            "gemini": GEMINI_MODEL
        }.get(used_provider, "default"),
        "note": error_note,
        "saved_to_astra": saved_to_astra,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def analyze_scrap_image(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    engine: str = "clip"
) -> Optional[Dict[str, Any]]:
    """
    Performs vision inspection using chosen engine:
      - 'clip': Zero-shot CLIP (handled in main.py)
      - 'openai': GPT-4o Vision
      - 'claude': Claude 3.5 Sonnet Vision
      - 'gemini' / 'astra': Gemini 1.5 Flash Vision
    """
    engine = engine.lower()
    if engine in ("clip", "local"):
        return None  # Let main.py run local CLIP

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    vision_prompt = (
        "Analyze this scrap or electronic waste item carefully. Identify the component or material type, "
        "estimated purity, potential precious metal recovery (gold, copper, silver), safety hazards, "
        "and market value in Indian Rupees. Output ONLY a valid JSON object with keys: "
        "detected_item (string), category (string: E-waste, Ferrous Metal, Non-Ferrous Metal, Plastic, Battery, etc), "
        "confidence (number 0-100), unit ('kg' or 'pcs'), min_price (number INR), max_price (number INR), "
        "price_range (string like '₹200 - ₹350 /kg'), reuse_tip (string), eco_impact (object with co2_saved_per_unit, energy_saved, badge), "
        "icon (single emoji)."
    )

    try:
        raw_text = ""
        if engine == "openai" and OPENAI_API_KEY:
            raw_text = call_openai_chat(vision_prompt, [], image_base64)
        elif engine == "claude" and ANTHROPIC_API_KEY:
            raw_text = call_claude_chat(vision_prompt, [], image_base64)
        elif (engine in ("gemini", "astra")) and GEMINI_API_KEY:
            raw_text = call_gemini_chat(vision_prompt, [], image_base64)

        if raw_text:
            # Extract JSON from code block if wrapped
            clean = raw_text.strip()
            if "```json" in clean:
                clean = clean.split("```json")[1].split("```")[0].strip()
            elif "```" in clean:
                clean = clean.split("```")[1].split("```")[0].strip()
            parsed = json.loads(clean)
            parsed["ai_engine"] = engine.upper()
            return parsed
    except Exception as e:
        print(f"[Vision Engine {engine}] Inference error: {e}", flush=True)

    return None
