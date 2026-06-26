import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def setup_cors(app: FastAPI):
    print("CORS setup")
    # Allow local development origins and specific frontend URL if set
    frontend_url = os.getenv("FRONTEND_URL", "https://web-production-f4e3d.up.railway.app")
    allowed_origins = [
        frontend_url,
        "http://localhost:5173",
        "http://localhost:3000",
        "https://multimodal-bot-frontend-bij2.vercel.app",
        "https://multimodal-bot-frontend-bij2.vercel.app/"
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins if os.getenv("ENVIRONMENT") == "production" else ["*"],
        allow_origin_regex=r"https://.*\.up\.railway\.app" if os.getenv("ENVIRONMENT") == "production" else None,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    