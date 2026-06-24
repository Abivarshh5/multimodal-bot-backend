from pydantic import BaseModel
from typing import List, Optional

class WebsiteRequest(BaseModel):
    url: str
    tenant_id: int = 1

class DataSourceRenameRequest(BaseModel):
    name: str

class SelectAllRequest(BaseModel):
    select: bool

class ChatMessage(BaseModel):
    role: str
    text: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    website_url: Optional[str] = None
    website_id: Optional[int] = None
    from_user: bool = True

class ProductRequest(BaseModel):
    description: str
    website_url: Optional[str] = None
