from fastapi import APIRouter
from app.controllers.branding_controller import get_website_branding
from app.models.branding_models import BrandProfileResponse

router = APIRouter()

@router.get("/data-sources/{id}/branding", response_model=BrandProfileResponse)
def get_branding_route(id: int):
    print("Branding route")
    return get_website_branding(id)
