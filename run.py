"""
============================================================
ScrapSense AI - Unified Application Launcher & Live Server
============================================================
This script starts both the FastAPI backend (port 8000) and
the Frontend Live Web Server (port 5500) concurrently with
automatic health monitoring and persistent always-on service.
============================================================
"""

import os
import sys
import time
import webbrowser
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

# Unbuffered UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


class CORSFrontendHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def log_message(self, format, *args):
        pass


def get_local_ip():
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            import socket
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except Exception:
            return "127.0.0.1"


def run_frontend_server(port=5500):
    try:
        server_address = ("0.0.0.0", port)
        httpd = HTTPServer(server_address, CORSFrontendHandler)
        httpd.serve_forever()
    except Exception as e:
        print(f"[!] Frontend server error: {e}", flush=True)


def run_backend_server(port=8000):
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        import uvicorn
        import main as backend_module
        config = uvicorn.Config(
            backend_module.app,
            host="0.0.0.0",
            port=port,
            loop="asyncio",
            log_level="warning"
        )
        server = uvicorn.Server(config)
        server.install_signal_handlers = lambda: None
        loop.run_until_complete(server.serve())
    except Exception as e:
        import traceback
        with open(os.path.join(ROOT_DIR, "backend_error.log"), "w", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        print(f"[!] Backend server error: {e}", flush=True)


def is_port_in_use(port):
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        res = s.connect_ex(("127.0.0.1", port))
        s.close()
        return res == 0
    except Exception:
        return False


def wait_for_backend(port=8000, attempts=60):
    health_url = f"http://127.0.0.1:{port}/health"
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(health_url, timeout=1.5) as response:
                if response.status == 200:
                    print("[✓] Backend health check passed · Status: Online", flush=True)
                    return True
        except Exception:
            time.sleep(0.5)
    print("[!] Backend startup took longer than expected, continuing in background...", flush=True)
    return False


def main():
    print("=" * 62, flush=True)
    print("  ♻️  ScrapSense AI - Smart Waste & Scrap Valuation Platform", flush=True)
    print("=" * 62, flush=True)

    # 1. Start Frontend Live Server on port 5500 in daemon thread
    if not is_port_in_use(5500):
        frontend_thread = threading.Thread(target=run_frontend_server, args=(5500,), daemon=True)
        frontend_thread.start()
        print("[*] Frontend Live Server active on port 5500", flush=True)
    else:
        print("[*] Port 5500 is already active (Live Server / VS Code)", flush=True)

    # 2. Start Backend FastAPI on port 8000 in daemon thread
    if not is_port_in_use(8000):
        backend_thread = threading.Thread(target=run_backend_server, args=(8000,), daemon=True)
        backend_thread.start()
        print("[*] Starting FastAPI Backend on port 8000...", flush=True)
        wait_for_backend(8000)
    else:
        print("[*] Backend port 8000 is already active", flush=True)

    local_ip = get_local_ip()
    print("\n" + "=" * 62, flush=True)
    print("  🚀 ScrapSense AI is LIVE & ALWAYS CONNECTED!", flush=True)
    print("=" * 62, flush=True)
    print(f"  💻 Laptop / PC   : http://127.0.0.1:8000 (Unified App + Backend)", flush=True)
    print(f"  📱 Mobile Phone  : http://{local_ip}:8000", flush=True)
    print(f"  ⚡ Live Server   : http://127.0.0.1:5500 (Alternative)", flush=True)
    print(f"  📖 API Docs      : http://127.0.0.1:8000/docs", flush=True)
    print("=" * 62 + "\n", flush=True)

    try:
        webbrowser.open("http://127.0.0.1:8000")
    except Exception:
        pass

    print("Servers running continuously. Press Ctrl+C to stop...\n", flush=True)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Stopping ScrapSense AI servers...", flush=True)
        sys.exit(0)


if __name__ == "__main__":
    main()
