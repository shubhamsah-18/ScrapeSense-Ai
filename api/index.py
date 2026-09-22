import os
import sys
from pathlib import Path

# Add root and backend directories to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Ensure DISABLE_TORCH is set for serverless environments
os.environ.setdefault("DISABLE_TORCH", "1")

# Expose the FastAPI ASGI application for Vercel
from backend.main import app
