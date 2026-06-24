from fastapi import APIRouter
from app.models.requests import ProductRequest
from app.controllers.product_controller import handle_find_products

router = APIRouter()

@router.post("/products")
async def find_products_endpoint(request_data: ProductRequest):
    return handle_find_products(request_data)
