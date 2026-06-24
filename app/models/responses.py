from pydantic import BaseModel
from typing import List, Optional, Any

class BaseResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    message: Optional[str] = None

class DataSourceResponse(BaseResponse):
    id: int
    url: str

class DataSourceListResponse(BaseResponse):
    dataSources: List[dict]

class PagesListResponse(BaseResponse):
    pages: List[dict]

class TrainingProgressResponse(BaseResponse):
    total_pages: int
    total_selected: int
    trained_count: int

class ChatResponse(BaseModel):
    reply: str
    open_camera: bool
    find_products: bool
    sources: List[dict] = []
