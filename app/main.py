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

@app.get("/reset-all", tags=["Diagnostics"])
def reset_all_route():
    from app.db.postgres import execute_query
    try:
        execute_query("DELETE FROM crawled_pages")
        execute_query("DELETE FROM crawl_status")
        execute_query("DELETE FROM brand_profile")
        execute_query("DELETE FROM websites")
        return {"status": "success", "message": "All data sources, pages, and statuses deleted successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/run-diag", tags=["Diagnostics"])
def run_diag_route():
    import subprocess
    import sys
    results = {}
    try:
        # 1. pip show patchright
        res1 = subprocess.run([sys.executable, "-m", "pip", "show", "patchright"], capture_output=True, text=True)
        results["pip_show_patchright"] = {"stdout": res1.stdout, "stderr": res1.stderr}
        
        # 2. pip show playwright
        res2 = subprocess.run([sys.executable, "-m", "pip", "show", "playwright"], capture_output=True, text=True)
        results["pip_show_playwright"] = {"stdout": res2.stdout, "stderr": res2.stderr}
        
        # 3. pip show playwright-stealth
        res3 = subprocess.run([sys.executable, "-m", "pip", "show", "playwright-stealth"], capture_output=True, text=True)
        results["pip_show_playwright_stealth"] = {"stdout": res3.stdout, "stderr": res3.stderr}
        
        # 4. pip show tf-playwright-stealth
        res4 = subprocess.run([sys.executable, "-m", "pip", "show", "tf-playwright-stealth"], capture_output=True, text=True)
        results["pip_show_tf_playwright_stealth"] = {"stdout": res4.stdout, "stderr": res4.stderr}
        
        # 5. python -c version checks
        res5 = subprocess.run([sys.executable, "-c", "import playwright; print(playwright.__version__)"], capture_output=True, text=True)
        results["playwright_version_import"] = {"stdout": res5.stdout, "stderr": res5.stderr}
        
        return results
    except Exception as e:
        return {"error": str(e)}

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
