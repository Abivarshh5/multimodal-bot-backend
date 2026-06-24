from fastapi import WebSocket
from app.services.websocket_service import handle_websocket_connection

async def handle_ws(websocket: WebSocket):
    await handle_websocket_connection(websocket)
