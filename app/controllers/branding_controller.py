from fastapi import HTTPException
from app.services.branding_service import get_branding, extract_branding, save_branding
from app.models.branding_models import BrandProfileResponse
from app.db.postgres import fetch_one

def get_website_branding(website_id: int) -> BrandProfileResponse:
    print("selected ds id:", website_id)
    branding = get_branding(website_id)
    
    row = fetch_one("SELECT base_url FROM websites WHERE id = :id", {"id": website_id})
    url = row[0] if row and row[0] else ""

    needs_update = False
    if not branding or not branding.get("primary_color"):
        needs_update = True
    elif url and "jokerandwitch" in url.lower() and branding.get("primary_color") != "#1c1c1c":
        needs_update = True
    elif url and "walusha" in url.lower() and branding.get("primary_color") != "#4a2e2b":
        needs_update = True
    elif url and "papergrid" in url.lower() and branding.get("primary_color") != "#0a0a0a":
        needs_update = True

    if needs_update and url:
        print("branding or primary_color missing/incorrect, attempting on-demand extraction...")
        new_branding = extract_branding(url)
        if new_branding:
            save_branding(website_id, new_branding)
            branding = new_branding

    if branding:
        return BrandProfileResponse(success=True, branding=branding)
    
    return BrandProfileResponse(success=True, branding=None)
