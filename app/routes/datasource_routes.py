from fastapi import APIRouter
from app.models.requests import WebsiteRequest, DataSourceRenameRequest
from app.controllers.datasource_controller import (
    add_website, get_data_sources, rename_data_source,
    delete_data_source, get_crawl_status, get_datasource_pages
)

router = APIRouter()

@router.post("/add-website")
async def add_website_endpoint(request_data: WebsiteRequest):
    return add_website(request_data)

@router.get("/data-sources")
async def get_data_sources_endpoint():
    return get_data_sources()

@router.put("/data-sources/{id}")
async def rename_data_source_endpoint(id: int, request_data: DataSourceRenameRequest):
    print("Data source renamed")
    return rename_data_source(id, request_data)

@router.delete("/data-sources/{id}")
async def delete_data_source_endpoint(id: int):
    print("Data source deleted", id)
    return delete_data_source(id)

@router.get("/crawl-status/{website_id}")
async def get_crawl_status_endpoint(website_id: int):
    return get_crawl_status(website_id)

@router.get("/data-sources/{id}/pages")
async def get_datasource_pages_endpoint(id: int):
    return get_datasource_pages(id)
