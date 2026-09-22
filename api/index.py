import os
import sys
from pathlib import Path
from starlette.responses import FileResponse, JSONResponse

# Add root and backend directories to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
PUBLIC_DIR = ROOT_DIR / "public"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Ensure DISABLE_TORCH is set for serverless environments
os.environ.setdefault("DISABLE_TORCH", "1")

# Import FastAPI app from backend.main
from backend.main import app

# Strip /api prefix if present so both /api/endpoint and /endpoint work seamlessly
class VercelPathNormalizerMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            
            # Normalize /api/ prefix
            if path.startswith("/api/"):
                scope["path"] = path[4:]
            elif path == "/api":
                scope["path"] = "/"
                
            # If root or index requested, ensure index.html is returned
            normalized_path = scope.get("path", "")
            if normalized_path in ("/", "/index.html", "/frontend/index.html"):
                index_path = PUBLIC_DIR / "index.html"
                if not index_path.exists():
                    index_path = FRONTEND_DIR / "index.html"
                if index_path.exists():
                    response = FileResponse(str(index_path), media_type="text/html")
                    await response(scope, receive, send)
                    return

        await self.app(scope, receive, send)

app.add_middleware(VercelPathNormalizerMiddleware)
