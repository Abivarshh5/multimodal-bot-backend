from fastapi import FastAPI
from app.core.config import *  # loads env vars early
from app.middleware.cors import setup_cors
import uvicorn
from app.middleware.error_handler import setup_error_handlers
from app.routes import (
    chat_routes,
    datasource_routes,
    training_routes,
    product_routes,
    websocket_routes,
    branding_routes
)

app = FastAPI(title="Multimodal Shopping Assistant API")

setup_cors(app)
setup_error_handlers(app)

import threading
import subprocess
import sys
from app.db.database import init_db

def install_browsers():
    try:
        print("Starting background browser installation...")
        subprocess.run([sys.executable, "-m", "patchright", "install"], check=True)
        print("Background browser installation completed successfully!")
    except Exception as e:
        print(f"Error during background browser installation: {e}")

@app.on_event("startup")
def on_startup():
    init_db()
    threading.Thread(target=install_browsers, daemon=True).start()

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

@app.get("/list-cache", tags=["Diagnostics"])
def list_cache_route():
    import os
    import pathlib
    try:
        home = pathlib.Path.home()
        cache_path = home / ".cache"
        
        result = []
        if cache_path.exists():
            for root, dirs, files in os.walk(cache_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, home)
                    size = os.path.getsize(full_path)
                    result.append(f"{rel_path} ({size} bytes)")
        else:
            result.append(f"Cache path {cache_path} does not exist")
            
        return {"home": str(home), "files": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/install-browser", tags=["Diagnostics"])
def install_browser_route(force: bool = False):
    import subprocess
    import sys
    try:
        print(f"Synchronous browser installation triggered (force={force})...")
        cmd = [sys.executable, "-m", "patchright", "install"]
        if force:
            cmd.append("--force")
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return {"status": "success", "stdout": res.stdout, "stderr": res.stderr}
    except subprocess.CalledProcessError as e:
        return {"status": "failed", "error": str(e), "stdout": e.stdout, "stderr": e.stderr}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

app.include_router(chat_routes.router, tags=["Chat"])
app.include_router(datasource_routes.router, tags=["Data Sources"])
app.include_router(training_routes.router, tags=["Training"])
app.include_router(product_routes.router, tags=["Products"])
app.include_router(websocket_routes.router, tags=["WebSocket"])
app.include_router(branding_routes.router, tags=["Branding"])
