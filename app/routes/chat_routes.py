from fastapi import APIRouter
from app.models.requests import ChatRequest
from app.controllers.chat_controller import handle_chat

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request_data: ChatRequest):
    return handle_chat(request_data)
