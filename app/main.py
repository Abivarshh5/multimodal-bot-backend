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

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

app.include_router(chat_routes.router, tags=["Chat"])
app.include_router(datasource_routes.router, tags=["Data Sources"])
app.include_router(training_routes.router, tags=["Training"])
app.include_router(product_routes.router, tags=["Products"])
app.include_router(websocket_routes.router, tags=["WebSocket"])
app.include_router(branding_routes.router, tags=["Branding"])
