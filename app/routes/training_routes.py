from fastapi import APIRouter
from app.models.requests import SelectAllRequest
from app.controllers.training_controller import (
    toggle_page_training, select_all_pages, delete_page,
    start_datasource_training, retrain_data_source,
    get_training_progress, get_training_status
)

router = APIRouter()

@router.put("/pages/{id}/training")
async def toggle_page_training_endpoint(id: int):
    return toggle_page_training(id)

@router.delete("/pages/{id}")
async def delete_page_endpoint(id: int):
    return delete_page(id)

@router.put("/data-sources/{id}/pages/select-all")
async def select_all_pages_endpoint(id: int, request_data: SelectAllRequest):
    return select_all_pages(id, request_data)

@router.post("/data-sources/{id}/train")
async def start_datasource_training_endpoint(id: int):
    return start_datasource_training(id)

@router.post("/data-sources/{id}/retrain")
async def retrain_data_source_endpoint(id: int):
    return retrain_data_source(id)

@router.get("/training-progress/{id}")
async def get_training_progress_endpoint(id: int):
    return get_training_progress(id)

@router.get("/training-status/")
async def get_training_status_endpoint(url: str):
    return get_training_status(url)
