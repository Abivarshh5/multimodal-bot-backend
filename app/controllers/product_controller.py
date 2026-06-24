from app.services.product_service import find_products
from app.models.requests import ProductRequest

def handle_find_products(request: ProductRequest) -> dict:
    return find_products(description=request.description, website_url=request.website_url)
