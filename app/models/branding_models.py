from pydantic import BaseModel
from typing import Optional

class BrandProfileModel(BaseModel):
    company_name: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    primary_color: Optional[str] = None

class BrandProfileResponse(BaseModel):
    success: bool
    branding: Optional[BrandProfileModel] = None
